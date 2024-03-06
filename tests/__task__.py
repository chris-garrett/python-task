from glob import glob
from __task__ import TaskContext, TaskBuilder


def _run(ctx: TaskContext):
    tests = "".join(glob(f"{ctx.root_dir}/tests/*_tests.py"))
    ctx.exec(f"pytest --lf -v --capture=tee-sys {tests}", cwd=ctx.project_dir)


def configure(builder: TaskBuilder):
    module_name = "tests"
    builder.add_task(module_name, f"{module_name}:run", _run)
