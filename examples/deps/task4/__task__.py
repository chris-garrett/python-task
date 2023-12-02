from __task__ import TaskContext, TaskBuilder


def _run(ctx: TaskContext):
    ctx.log.info("Task4")


def configure(builder: TaskBuilder):
    module_name = "deps:task4"
    builder.add_task(module_name, "deps:task4", _run, deps=["deps:task1"])
