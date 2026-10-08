"""The runtime's words the wire is written in: JSON, the worlds, the channels, a quota."""

from typing import Literal, TypeAlias

from typing_extensions import TypeAliasType

# A recursive alias needs a name of its own: pydantic and pyright both read TypeAliasType.
Json = TypeAliasType("Json", "str | int | float | bool | list[Json] | dict[str, Json] | None")

JsonObject: TypeAlias = dict[str, Json]

# A key belongs to one world; its agents, numbers and calls are isolated to it.
Env: TypeAlias = Literal["production", "sandbox"]

# phone: SIP into a LiveKit room; web: the widget over WebRTC; whatsapp: text.
Channel: TypeAlias = Literal["phone", "web", "whatsapp"]

# How the call is had: spoken (a room, a voice) or written (a text session); `web` is either.
Medium: TypeAlias = Literal["voice", "text"]

Direction: TypeAlias = Literal["inbound", "outbound"]

# app: the tenant's backend. participant: the caller's browser.
EventSource: TypeAlias = Literal["app", "participant"]

QuotaName: TypeAlias = Literal[
    "minutes",
    "messages",
    "agents",
    "concurrent_calls",
    "memory_facts",
    "knowledge_chunks",
    "numbers",
    "seats",
    "llm_tokens",
    "hosted_apps",
    "budget_usd",
]
