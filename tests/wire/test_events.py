"""Tests for the registry of events: every entry of the golden log reads as the model it names."""

import pytest

from pinecall.errors import WireError
from pinecall.wire.events import EPHEMERAL_EVENTS, EVENTS, TERMINAL_EVENT, event_of
from pinecall.wire.frames import Entry
from tests.wire.golden import golden_entries


def test_the_ephemeral_events_and_the_terminal_one_are_registered() -> None:
    assert set(EVENTS) >= EPHEMERAL_EVENTS
    assert TERMINAL_EVENT in EVENTS


def test_every_entry_of_the_golden_log_is_the_model_its_type_names() -> None:
    entries = golden_entries()
    for entry in entries:
        assert type(event_of(entry)) is EVENTS[entry.type]
    assert [entry.type for entry in entries if not entry.ephemeral][-1] == TERMINAL_EVENT


def test_an_entry_of_a_type_nobody_declared_is_refused_with_its_name() -> None:
    entry = Entry(
        seq=1, ts=1.0, call="c", agent="a", type="call.imagined", ephemeral=False, data={}
    )
    with pytest.raises(WireError, match=r"unknown event type: call\.imagined"):
        event_of(entry)
