from newsroom.commands import * # noqa
from newsroom.commands.manager import manager

from cp.commands.fix_language import fix_language  # noqa


if __name__ == "__main__":
    manager.run()
