from __tasklib__ import TaskContext, TaskBuilder


def _info(ctx: TaskContext):
    ctx.log.info(f"Platform: {ctx.system.platform}")
    ctx.log.info(f"Architecture: {ctx.system.arch}")
    ctx.log.info(f"Distribution: {ctx.system.distro}")


def configure(builder: TaskBuilder):
    module_name = "platform"
    builder.add_task(module_name, "platform:info", _info)
