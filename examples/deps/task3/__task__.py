from __task__ import TaskContext, TaskBuilder


def _run(ctx: TaskContext):
    ctx.log.info("Task3")


def configure(builder: TaskBuilder):
    module_name = "deps:task3"
    builder.add_task(module_name, "deps:task3", _run, deps=["deps:task1", "deps:task2", "deps:task4"])
