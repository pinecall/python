"""`Agent`, the class a tenant writes: annotated fields are the state, `@tool` methods the verbs."""

import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar, Self

from pinecall import _accepts, _author, _config, _state, _tools
from pinecall._state import Change
from pinecall.errors import ToolFailed
from pinecall.wire._names import EventSource
from pinecall.wire.parts import ToolSpec


@dataclass(frozen=True)
class Logged:
    """One named line the agent appended to its call's log."""

    seq: int
    name: str
    data: object
    at: float


class Agent:
    """The base of an agent: its fields are the state, its tools the model's verbs.

    ```python
    class Front(Agent):
        \"\"\"You answer the phone for the business.\"\"\"

        stage: Literal["ask", "done"] = "ask"
        message: dict | None = None

        @tool(stage="ask", pii=("name",))
        def take_message(self, name: str, about: str) -> dict:
            \"\"\"Writes down who called and what about.\"\"\"
            self.message = {"name": name, "about": about}
            self.stage = "done"
            return self.message
    ```

    Every annotated attribute whose name does not start with `_` and that is not a `ClassVar` is
    a state field; a public `@property` is a derived one. Only a tool or a hook may write a field
    once the agent is sealed.
    """

    slug: ClassVar[str | None] = None
    """The name the agent registers as; the CLI passes the folder's, and refuses another."""

    channel_rules: ClassVar[bool] = True
    """`False` leaves the `<channel>` part out of the prompt."""

    view_template: ClassVar[str | None] = None
    """The view's Jinja, written here; left out, `views/<slug>.jinja` beside the class's file."""

    accepts: ClassVar[Mapping[str, Sequence[EventSource]]] = {}
    """The outside events the agent takes, and from whom: `{"slot.released": ["app"]}`."""

    _pinecall_fields: ClassVar[_state.Fields] = _state.Fields({}, (), None)
    _pinecall_events: ClassVar[dict[str, tuple[EventSource, ...]]] = {}
    _pinecall_tools: ClassVar[dict[str, _tools.Declared]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Read the class once, as it is created, and refuse what the gateway would refuse."""
        super().__init_subclass__(**kwargs)
        _config.refuse_the_worlds(cls)
        cls._pinecall_fields = _state.fields_of(cls, Agent, cls._pinecall_fields)
        cls._pinecall_events = _accepts.accepted(cls, cls._pinecall_events)
        cls._pinecall_tools = _tools.declared_tools(
            cls, Agent, cls._pinecall_tools, cls._pinecall_fields.stages
        )

    # ── the state ──

    def seal(self) -> Self:
        """Start recording: a write needs an author, and the values now are the baseline."""
        _state.store_of(self).sealed = True
        return self

    @property
    def sealed(self) -> bool:
        """Whether writes are being recorded."""
        return _state.store_of(self).sealed

    def snapshot(self) -> dict[str, object]:
        """The state now, derived fields included."""
        values = dict(_state.store_of(self).values)
        return values | {name: getattr(self, name) for name in self._pinecall_fields.derived}

    def restore(self, state: Mapping[str, object]) -> Self:
        """Replace the state with `state`; a field it leaves out is cleared to None."""
        with _author.writing_as(_author.current() or "restore"):
            for name in self._pinecall_fields.declared:
                _state.write(self, name, state.get(name))
        return self

    def start_in(self, state: Mapping[str, object]) -> Self:
        """Set the fields `state` names over the rest, which keep their values."""
        return self.restore(dict(_state.store_of(self).values) | dict(state))

    def changes(self) -> list[Change]:
        """Every recorded write since the agent was sealed, oldest first."""
        return list(_state.store_of(self).changes)

    def on_change(self, listener: Callable[[Change], None]) -> Callable[[], None]:
        """Call `listener` with every recorded write; the answer stops it."""
        listeners = _state.store_of(self).listeners
        listeners.append(listener)
        return lambda: listeners.remove(listener)

    def collapse(self, summary: str) -> None:
        """Replace the recorded writes with one sentence saying what they came to."""
        _state.collapsed(_state.store_of(self), summary)

    # ── the tools ──

    def tools(self) -> list[ToolSpec]:
        """Every tool the class declares, as the gateway receives it, seen or not."""
        return [declared.spec for declared in self._pinecall_tools.values()]

    def visible_tools(self) -> list[ToolSpec]:
        """The tools the model sees in the state now."""
        return [
            declared.spec
            for declared in self._pinecall_tools.values()
            if _tools.shows(declared, self)
        ]

    def run_tool(self, name: str, arguments: Mapping[str, object] | None = None) -> object:
        """Run a tool as a call does: its arguments checked, its writes authored, its answer cut.

        Args:
            name: the tool's name.
            arguments: the object the model sends, by parameter name.
        """
        declared = self._pinecall_tools.get(name)
        if declared is None:
            raise ToolFailed(f"{name}: this agent declares no such tool")
        return _tools.ran(self, declared, arguments or {})

    # ── the log ──

    def log(self, name: str, data: object = None) -> Logged:
        """Append a named line to the call's log: the platform keeps it and never reads it."""
        line = Logged(_state.store_of(self).next_seq(), name, data, time.time())
        kept = _log_of(self)
        kept.lines.append(line)
        for listener in list(kept.listeners):
            listener(line)
        return line

    def logged(self) -> list[Logged]:
        """Every line the agent logged, oldest first."""
        return list(_log_of(self).lines)

    def on_log(self, listener: Callable[[Logged], None]) -> Callable[[], None]:
        """Call `listener` with every line logged; the answer stops it."""
        listeners = _log_of(self).listeners
        listeners.append(listener)
        return lambda: listeners.remove(listener)


@dataclass
class _Log:
    lines: list[Logged]
    listeners: list[Callable[[Logged], None]]


def _log_of(agent: Agent) -> _Log:
    kept: _Log = vars(agent).setdefault("_pinecall_log", _Log([], []))
    return kept
