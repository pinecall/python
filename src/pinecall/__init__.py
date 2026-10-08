"""The door: what `import pinecall` gives a person writing an agent, and nothing else."""

from pinecall._version import __version__ as __version__
from pinecall.errors import PinecallError as PinecallError
from pinecall.errors import WireError as WireError

__all__ = ["PinecallError", "WireError", "__version__"]


def _owned_by_the_door() -> None:
    # A traceback names `pinecall.PinecallError`, what a person imports, not its private module.
    for name in __all__:
        exported = globals()[name]
        if isinstance(exported, type):
            exported.__module__ = __name__


_owned_by_the_door()
