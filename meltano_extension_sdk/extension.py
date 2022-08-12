"""Meltano extension SDK base class and supporting methods."""
from __future__ import annotations

import json
import sys
from abc import ABCMeta, abstractmethod
from enum import Enum

import structlog
import yaml

from meltano_extension_sdk import models


class DescribeFormat(str, Enum):
    text = "text"
    json = "json"
    yaml = "yaml"


class ExtensionBase(metaclass=ABCMeta):
    """Basic extension interface that must be implemented by all extensions."""

    def pre_invoke(self):
        """Called before the extension is invoked."""
        pass

    def initialize(self, force: bool = False):
        """Initialize the extension.

        This method is called on-demand by the user to initialize the extension.
        Extensions are not required to implement this method, and may no-op.

        Args:
            force: If True, force initialization.
        """
        pass

    @abstractmethod
    def invoke(self, command_name: str | None, *command_args) -> None:
        """Invoke method.

        This method is called when the extension is invoked.
        """
        pass

    def post_invoke(self):
        """Called after the extension is invoked."""
        pass

    @abstractmethod
    def describe(self) -> models.Describe:
        """Describe method.

        This method should describe what commands & capabilities the extension provides.

        Returns:
            Description: A description of the extension.
        """
        pass

    def describe_formatted(
        self, output_format: DescribeFormat = DescribeFormat.text
    ) -> str:
        """Return a formatted description of the extensions commands and capabilities.

        Args:
            output_format: The output format to use.

        Returns:
            str: The formatted description.
        """
        if output_format == DescribeFormat.text:
            return f"{self.describe()}"
        elif output_format == DescribeFormat.json:
            return self.describe().json(indent=2)
        elif output_format == DescribeFormat.yaml:
            # just calling describe().dict() and dumping that to yaml yields a yaml that is subtly
            # different to the json variant in that it you have an additional level of nesting.
            return yaml.dump(
                yaml.safe_load(self.describe().json()), sort_keys=False, indent=2
            )

    def pass_through_invoker(
        self, logger: structlog.BoundLogger, *command_args
    ) -> None:
        """Pass-through invoker.

        This method is used to invoke the wrapped CLI with arbitrary arguments.
        Note this method will hard exit the process if an unhandled exception is
        encountered.

        Args:
            logger: The logger to use in the event an exception needs to be logged.
            *command_args: The arguments to pass to the command.
        """
        logger.debug(
            "pass through invoker called",
            command_args=command_args,
        )
        try:
            self.pre_invoke()
        except Exception:
            logger.exception(
                "pre_invoke failed with uncaught exception, please report to maintainer"
            )
            sys.exit(1)

        try:
            self.invoke(None, command_args)
        except Exception:
            logger.exception(
                "invoke failed with uncaught exception, please report to maintainer"
            )
            sys.exit(1)

        try:
            self.post_invoke()
        except Exception:
            logger.exception(
                "post_invoke failed with uncaught exception, please report to maintainer"
            )
            sys.exit(1)
