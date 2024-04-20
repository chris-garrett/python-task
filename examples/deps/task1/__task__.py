from __tasklib__ import TaskContext, TaskBuilder


def _run(ctx: TaskContext):
    ctx.log.info("Task1")


def configure(builder: TaskBuilder):
    module_name = "deps:task1"
    builder.add_task(module_name, "deps:task1", _run)
