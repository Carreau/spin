import os
import sys
from glob import glob

import click
import toml

from . import cmds
from .cmds import *


class DotDict(dict):
    def __getitem__(self, key):
        subitem = self
        for subkey in key.split('.'):
            try:
                subitem = dict.__getitem__(subitem, subkey)
            except KeyError:
                raise KeyError(f'`{key}` not found in configuration') from None
        return subitem


if __name__ == "__main__":
    if not os.path.exists("pyproject.toml"):
        print("Error: cannot find [pyproject.toml]")
        sys.exit(1)

    with open("pyproject.toml") as f:
        try:
            toml_config = toml.load(f)
        except:
            print("Cannot parse [pyproject.toml]")
            sys.exit(1)

    try:
        project_config = toml_config["project"]
    except KeyError:
        print("No project section found in pyproject.toml")
        sys.exit(1)

    try:
        config = toml_config["tool"]["dev"]["py"]
    except KeyError:
        print("No configuration found in [pyproject.toml] for [tool.dev.py]")
        sys.exit(1)

    commands = {
        f"dev.py.{name}": getattr(cmds, name)
        for name in dir(cmds)
        if not name.startswith("_")
    }

    @click.group(help=f"Developer tool for {project_config['name']}")
    @click.pass_context
    def group(ctx):
        ctx.meta['config'] = DotDict(toml_config)

    for cmd in config["commands"]:
        group.add_command(commands[cmd])

    group()
