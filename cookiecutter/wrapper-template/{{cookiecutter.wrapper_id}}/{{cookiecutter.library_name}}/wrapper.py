from __future__ import annotations

import os
import pkgutil
import subprocess
import sys
from pathlib import Path

import structlog

from meltano_extension_sdk import models
from meltano_extension_sdk.extension import ExtensionBase
from meltano_extension_sdk.process import Invoker, log_subprocess_error

log = structlog.get_logger()


class {{ cookiecutter.source_name }}(ExtensionBase):

    def __init__(self):
        self.{{ cookiecutter.extension_name }}_bin = "{{ cookiecutter.wrapper_target_name }}" # verify this is the correct name
        self.{{ cookiecutter.extension_name }}_invoker = Invoker(self.{{ cookiecutter.extension_name }}_bin)

    def invoke(self, command_name: str | None, *command_args):
        """Invoke the underlying cli, that is being wrapped by this extension."""
        try:
            self.{{ cookiecutter.extension_name }}_invoker.run_and_log(command_name, *command_args)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                f"{{ cookiecutter.extension_name }} {command_name}", err, "{{ cookiecutter.extension_name }} invocation failed"
            )
            sys.exit(err.returncode)

    def describe(self) -> models.Describe:
        # TODO: could we auto-generate all or portions of this from typer instead?
        return models.Describe(
            commands=[
                models.ExtensionCommand(
                    name="{{ cookiecutter.cli_prefix }}_extension", description="extension commands"
                ),
                models.InvokerCommand(
                    name="{{ cookiecutter.cli_prefix }}_invoker", description="pass through invoker"
                ),
            ]
        )