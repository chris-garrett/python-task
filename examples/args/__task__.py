from __tasklib__ import TaskContext, TaskBuilder


def _hello(ctx: TaskContext):
    ctx.log.info(f"Args: {ctx.args}")


def configure(builder: TaskBuilder):
    module_name = "args"
    builder.add_task(module_name, "args:hello", _hello)
