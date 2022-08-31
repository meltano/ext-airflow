from typing import List

from pydantic import BaseModel


class Command(BaseModel):
    name: str
    description: str
    commands: List[str] = []
    pass_through_cli: bool = False


class ExtensionCommand(Command):
    description = "The extension cli"
    pass_through_cli: bool = False
    commands: List[str] = [
        "describe",
        "invoke",
        "pre_invoke",
        "post_invoke",
        "initialize",
    ]


class InvokerCommand(Command):
    description = "The pass through invoker cli"
    pass_through_cli: bool = True
    commands: List[str] = [":splat"]


class Describe(BaseModel):
    commands: List[Command]
