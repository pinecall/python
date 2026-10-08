"""The door: what `import pinecall` gives a person writing an agent, and nothing else."""

from pinecall._state import Change as Change
from pinecall._state import state as state
from pinecall._version import __version__ as __version__
from pinecall.agent import Agent as Agent
from pinecall.agent import Logged as Logged
from pinecall.errors import DeclarationRefused as DeclarationRefused
from pinecall.errors import NotAStage as NotAStage
from pinecall.errors import PinecallError as PinecallError
from pinecall.errors import ToolFailed as ToolFailed
from pinecall.errors import UnauthoredWrite as UnauthoredWrite
from pinecall.errors import WireError as WireError

__all__ = [
    "Agent",
    "Change",
    "DeclarationRefused",
    "Logged",
    "NotAStage",
    "PinecallError",
    "ToolFailed",
    "UnauthoredWrite",
    "WireError",
    "__version__",
    "state",
]


def _owned_by_the_door() -> None:
    # A traceback names `pinecall.PinecallError`, what a person imports, not its private module.
    for name in __all__:
        exported = globals()[name]
        if isinstance(exported, type):
            exported.__module__ = __name__


_owned_by_the_door()
