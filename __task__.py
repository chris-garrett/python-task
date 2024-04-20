from __tasklib__ import TaskContext, TaskBuilder


def _hello(ctx: TaskContext):
    ctx.log.info("Hello")


def configure(builder: TaskBuilder):
    module_name = "root"
    builder.add_task(module_name, "hello", _hello)
    builder.add_task(module_name, "world", lambda ctx: ctx.log.info("World"))
