from __task__ import TaskContext, TaskBuilder


def _run(ctx: TaskContext):
    ctx.log.info("Task2")


def configure(builder: TaskBuilder):
    module_name = "deps:task2"
    builder.add_task(module_name, module_name, _run, deps=["deps:task1"])
