"""What a class may still say about itself, and the world's settings it is refused at creation."""

import re

from pinecall._state import own_annotations
from pinecall.errors import DeclarationRefused

# Settings that are the world's, each with the verb that sets it. Word for word the TypeScript
# package's `THE_WORLDS` and the gem's `Config::THE_WORLDS`.
THE_WORLDS: dict[str, str] = {
    "voice": "pinecall agent set --voice <name>",
    "llm": "pinecall agent set --llm <vendor/model>",
    "stt": "pinecall agent set --stt <vendor>",
    "language": "pinecall agent set --language <tag>",
    "greeting": "pinecall agent set --greeting '…' (or --reply '…')",
    "hangup": "pinecall agent set --hangup '…'",
    "says": "pinecall lexicon add <word> --say '…'",
    "hears": "pinecall lexicon hear <word> …",
    "memory": "pinecall memory policy --remember '…' --forget '…'",
    "record": "pinecall agent set --record on|off",
    "knowledge": (
        "pinecall agent knowledge edit — what the agent knows by heart is a setting, not a file"
    ),
    "docs": "pinecall docs push, then pinecall docs attach <base>",
}


def moved_to_the_world(field: str) -> str:
    """The sentence a class that declares one of the world's settings is refused with."""
    return (
        f"`{field}` is the world's now, not the class's: {THE_WORLDS[field]}"
        " — remove it from the class"
    )


def refuse_the_worlds(cls: type) -> None:
    """Refuse a class that sets or annotates one of the world's settings, naming the verb."""
    written = set(vars(cls)) | set(own_annotations(cls))
    for field in THE_WORLDS:
        if field in written:
            raise DeclarationRefused(moved_to_the_world(field))


def slug_of(cls: type) -> str:
    """The slug the class names itself with `slug = "…"`, else its name in kebab-case."""
    named = getattr(cls, "slug", None)
    if isinstance(named, str):
        return named
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", cls.__name__)
    return re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", spaced).lower()
