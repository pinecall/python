"""What the serve entry prints: an entry a line for the CLI, a line for a person, the drain."""

import json
from typing import TextIO

from pinecall.client import Client, Drained
from pinecall.wire.frames import Entry


def entry_line(entry: Entry) -> str:
    """One entry as the CLI reads it: `{type, agent, call, data}`, data as the gateway wrote it."""
    return json.dumps(
        {"type": entry.type, "agent": entry.agent, "call": entry.call, "data": entry.data},
        ensure_ascii=False,
    )


def said(client: Client, out: TextIO, err: TextIO, *, events: bool) -> None:
    """Listen before connecting, so `agent.registered` is a pipe's first line; flush each one."""

    def heard(entry: Entry) -> None:
        if events:
            out.write(entry_line(entry) + "\n")
        elif entry.type == "agent.registered":
            out.write(f"{entry.agent}  · answering as {entry.data.get('app')}\n")
        # A pipe's stdout is block-buffered: unflushed, the CLI waiting on a line sees it at exit.
        out.flush()

    def failed(error: Exception) -> None:
        err.write(f"{type(error).__name__}: {error}\n")
        err.flush()

    client.on_entries(heard)
    client.on_errors(failed)


def drain_line(drained: Drained) -> str:
    """Where the calls went, and what became of the tools running: one line."""
    if drained.handed + drained.parked + drained.tools == 0:
        return "draining · no live calls"
    parts = ["draining"]
    if drained.handed:
        parts.append(f"{plural(drained.handed, 'live call')} handed over")
    if drained.parked:
        parts.append(f"{plural(drained.parked, 'live call')} kept for the next process")
    if drained.finished:
        parts.append(f"{plural(drained.finished, 'tool')} finished")
    if drained.tools > drained.finished:
        parts.append(f"{plural(drained.tools - drained.finished, 'tool')} cut")
    return " · ".join(parts)


def plural(count: int, noun: str) -> str:
    """`1 tool`, `2 tools`."""
    return f"{count} {noun}{'' if count == 1 else 's'}"
