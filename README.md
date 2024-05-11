# python-task

My personal task runner.


## Quick Start

1. Copy `task` and `__tasklib__.py` to the root of your project
2. Create a `__task__.py` somewhere in your project like `foo/__task__.py`. 
    ```
    from __tasklib__ import TaskContext, TaskBuilder


    def _hello(ctx: TaskContext):
        ctx.log.info("Hello")


    def configure(builder: TaskBuilder):
        module_name = "foo"
        builder.add_task(module_name, "hello", _hello)
        builder.add_task(module_name, "world", lambda ctx: ctx.log.info("World"))
    ```

Bash/Git Bash

1. Run `task` to see what's available
    ```
    $ ./task 
    2024-01-20 17:26:44,216 - task - INFO - Processing tasks
    usage: task [-h] [task ...]

    arguments:
    hello
    world


    options:
    -h, --help  show this help message and exit
    -v, --verbose  enabled debug logging
    ```
2. Run `task` with several targets
    ```
    $ ./task hello world
    2024-01-20 17:26:57,368 - task - INFO - Processing tasks
    2024-01-20 17:26:57,374 - foo - INFO - Hello
    2024-01-20 17:26:57,374 - foo - INFO - World
    ```
