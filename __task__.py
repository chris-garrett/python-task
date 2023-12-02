#
# Nov 13 2023
# * initial cut of a task runner
#
# TODO
# * add dependency graph
#

import os
import re
import sys
import glob
import shlex
import typing
import logging
import platform
from logging import Logger
import argparse
from argparse import ArgumentParser
import subprocess
from subprocess import CompletedProcess
from typing import NamedTuple, Callable, List
import importlib.machinery
import inspect

env_files = [
    ".env.defaults",
    ".env.user",
    ".env.local",
    ".env",
]


def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kws)


TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")
logging.Logger.trace = trace

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("task")


def load_dotenv(filename):
    rx_env = re.compile(r"(\${?(\w+)}?)")
    if not os.path.exists(filename):
        return

    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue

            k, v = line.split("=", 1)
            match = re.search(rx_env, v)

            if match and (env := match.group(2)) in os.environ:
                v = v.replace(match.group(1), os.environ[env])

            os.environ[k] = v


for env in env_files:
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), env)))


class SystemContext(NamedTuple):
    platform: str  # Linux, Darwin, Windows
    arch: str  # x86_64, arm64
    distro: str  # Debian, Arch, RHEL


class TaskContext(NamedTuple):
    root_dir: str
    project_dir: str
    log: Logger
    exec: Callable[[str, [str | None], [Logger | None], [str | None]], CompletedProcess[str]]
    system: SystemContext


class TaskFileDefinition(NamedTuple):
    func: Callable[[TaskContext], None]  # configure func
    filename: str
    dir: str


class TaskDefinition(NamedTuple):
    func: Callable[[TaskContext], None]  # task func
    module: str
    name: str
    filename: str
    dir: str


class TaskBuilder(object):
    def __init__(self):
        self.parsers = []
        self.python_exe = "python"

    def use_python(self, python_exe):
        self.python_exe = python_exe

    def add_task(self, module: str, name: str, func: callable) -> None:
        """
        Add a task to the list of parsers.

        Args:
        - module (str): The name of the module containing the task.
        - name (str): The name of the task.
        - func (callable): The function that implements the task.
        """
        self.parsers.append((module, name, func))


def _build_env(env, venv_dir):
    """
    Replaces an old virtual env dir from path with a project
    level virtual env dir
    """
    old_env = env.copy()

    if "VIRTUAL_ENV" in old_env:
        old_venv = f"{old_env['VIRTUAL_ENV']}/bin:"
        # remove the old virtualenv path
        old_path = old_env["PATH"][len(old_venv) :]
    else:
        old_path = old_env["PATH"]

    # remove pythopath if it exists
    if "PYTHONHOME" in old_env:
        del old_env["PYTHONHOME"]

    new_venv = f"{venv_dir}/bin"

    # replace it with project virt env dir
    old_env["PATH"] = f"{new_venv}:{old_path}"

    # replace virt env
    old_env["VIRTUAL_ENV"] = new_venv

    return old_env


def exec(cmd: str, cwd=None, logger: Logger = None, venv_dir: str = None) -> CompletedProcess[str]:
    args = [arg.strip() for arg in shlex.split(cmd.strip())]
    if isinstance(logger, Logger):
        logger.debug("Executing: [%s] Cwd: [%s]", args, cwd)

    return subprocess.run(
        args,
        check=False,
        text=True,
        cwd=cwd,
        env=_build_env(os.environ, venv_dir) if venv_dir else os.environ,
    )


def _ensure_venv(ctx: TaskContext):
    if not os.path.exists(ctx.venv_dir):
        ctx.log.info(f"Creating venv {ctx.venv_dir}")
        ctx.exec([ctx.python_exe, "-m", "venv", ctx.venv_dir])


def _load_tasks(task: TaskFileDefinition) -> typing.Dict[str, TaskDefinition]:
    """
    Builds a list of N tasks based on what was specified in configure().
    """
    tasks: typing.Dict[str, TaskDefinition] = {}
    builder = TaskBuilder()
    task.func(builder)
    for module, name, func in builder.parsers:
        tasks[name] = TaskDefinition(module=module, name=name, func=func, dir=task.dir, filename=task.filename)
    return tasks


def _load_task_definitions(task_files) -> List[TaskFileDefinition]:
    """
    Loads tasks files if they match the required signature.
    """
    tasks: List[TaskFileDefinition] = []

    for idx, task_file in enumerate(task_files):
        loader = importlib.machinery.SourceFileLoader(f"task{idx}", task_file)
        module = loader.load_module()
        if not hasattr(module, "configure"):
            logger.trace(f"load task definition: {task_file}: no configure() found, skipping {task_file}")
            continue

        func = getattr(module, "configure")
        parameters = inspect.signature(func).parameters
        if "builder" not in parameters:
            logger.trace(f"load task definition: {task_file}: no configure(builder) found, skipping {task_file}")
            continue

        logger.trace(f"load task definition: {task_file}: loaded successfully")
        tasks.append(
            TaskFileDefinition(
                func=func,
                filename=task_file,
                dir=os.path.abspath(os.path.dirname(task_file)),
            )
        )

    return tasks


def _find_task_files() -> List[str]:
    """
    Finds files that match naming convention
    """
    return [f for f in glob.glob("**/__task__.py", recursive=True) if os.path.isfile(f) and f != "__task__.py"]


def _build_system_context() -> SystemContext:
    """
    Builds a context object for the system.
    """

    distro = ""
    if platform.system() == "Linux" and os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("ID="):
                    distro = line.split("=")[1].strip()
                    break

    return SystemContext(
        platform=platform.system().lower(),
        arch=platform.machine().lower(),
        distro=distro.lower(),
    )


def _build_task_context(task: TaskDefinition) -> TaskContext:
    """
    Builds a context object for a task.
    """
    return TaskContext(
        root_dir=os.path.abspath(os.path.dirname(__file__)),
        project_dir=task.dir,
        log=logging.getLogger(task.module),
        exec=exec,
        system=_build_system_context(),
    )


def _print_help(available_tasks: List[str]):
    # do a lazy sort to put tasks with no colons first
    formatted_tasks = "".join(
        [f"  {t}\n" for t in sorted(available_tasks, key=lambda x: (0 if x.count(":") == 0 else 1, x))]
    )
    print(
        f"""usage: task [-h] [task ...]

arguments:
{formatted_tasks}

options:
  -h, --help  show this help message and exit
  -v, --verbose  enabled debug logging
"""
    )


def _process_tasks():
    # need to boostrap this arg so that we can enable debug logging at
    # configure time
    raw_args = sys.argv[1:]
    if "-v" in raw_args or "--verbose" in raw_args:
        logger.setLevel(logging.DEBUG)

    task_files = _find_task_files()
    task_defs = _load_task_definitions(task_files)
    tasks: typing.Dict[str, TaskDefinition] = {}  # { 'task_name': TaskDefinition }

    parser = argparse.ArgumentParser(description="task", add_help=False)
    parser.add_argument("tasks", nargs="*")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")

    # configure tasks
    for task_def in task_defs:
        tasks.update(_load_tasks(task_def))

    args = parser.parse_args()

    if len(args.tasks) == 0 or args.help:
        _print_help(tasks.keys())
        return

    # validate tasks
    for task_name in args.tasks:
        if task_name not in tasks:
            logger.error("Unknown task: %s", task_name)
            _print_help(tasks.keys())
            return

    # runtime
    for task_name in args.tasks:
        if task_name in tasks:
            task = tasks[task_name]
            try:
                task.func(_build_task_context(task))
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    _process_tasks()
