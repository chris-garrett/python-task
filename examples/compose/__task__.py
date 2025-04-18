import os
from __tasklib__ import TaskContext, TaskBuilder

module_name = "tiny"


def _prefix(ctx: TaskContext, no_profiles: bool = False):
    profiles = "--profile all" if not no_profiles else ""
    compose_file = os.path.relpath(
        os.path.join(ctx.project_dir, "docker-compose.yml"), os.curdir
    )
    return f"docker compose -f {compose_file} {profiles}"


def _up(ctx: TaskContext):
    ctx.log.info("Starting docker-compose")
    ctx.exec(f"{_prefix(ctx)} up -d --remove-orphans")


def _down(ctx: TaskContext):
    ctx.log.info("Stopping docker-compose")
    ctx.exec(f"{_prefix(ctx, no_profiles=True)} stop")
    ctx.exec(f"{_prefix(ctx, no_profiles=True)} rm -f")


def _logs(ctx: TaskContext):
    ctx.log.info("Showing docker-compose logs")
    ctx.exec(f"{_prefix(ctx)} logs -f --tail 100")


def _restart(ctx: TaskContext):
    _down(ctx)
    _up(ctx)


def _pull(ctx: TaskContext):
    ctx.log.info("Pulling docker-compose images ")
    ctx.exec(
        "docker login ghcr.io -u USERNAME --password-stdin",
        input=os.getenv("GITHUB_TOKEN"),
    )
    ctx.exec(f"{_prefix(ctx)} pull")


def _nuke(ctx: TaskContext):
    ctx.log.info(f"Removing containers/volumes/ for {module_name}")
    _down(ctx)
    ret = ctx.exec(
        f"docker volume ls --filter 'name={module_name}*' --format '{{{{.Name}}}}'",
        capture=True,
    )
    if ret.returncode != 0:
        ctx.log.error("Failed to list volumes")
        return
    for volume in ret.stdout.splitlines():
        ctx.exec(f"docker volume rm {volume}")


def configure(builder: TaskBuilder):
    builder.add_task(module_name, "up", _up)
    builder.add_task(module_name, "down", _down)
    builder.add_task(module_name, "log", _logs)
    builder.add_task(module_name, "restart", _restart)
    builder.add_task(module_name, "pull", _pull)
    builder.add_task(module_name, "nuke", _nuke)
