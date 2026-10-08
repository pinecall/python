"""The base class: a subclass's own `__init__` keeps the state, and the log is the agent's own."""

from pinecall import Agent


class ConAgenda(Agent):
    """Una clínica con su propia agenda."""

    patient: str | None = None

    def __init__(self, agenda: str) -> None:
        """Keep the agenda this clinic books in."""
        self.agenda = agenda


def test_a_subclass_with_an_init_of_its_own_still_opens_its_state() -> None:
    agent = ConAgenda("la de prueba")
    assert (agent.agenda, agent.patient) == ("la de prueba", None)
    assert agent.snapshot() == {"patient": None}


def test_a_logged_line_is_kept_in_order_and_heard_until_the_listener_stops() -> None:
    agent = ConAgenda("x").seal()
    heard: list[str] = []
    stop = agent.on_log(lambda line: heard.append(line.name))
    agent.log("appointment.booked", {"when": "martes 10:00"})
    stop()
    agent.log("sms.sent")
    assert [(line.name, line.data) for line in agent.logged()] == [
        ("appointment.booked", {"when": "martes 10:00"}),
        ("sms.sent", None),
    ]
    assert heard == ["appointment.booked"]


def test_a_class_that_is_not_sealed_says_so() -> None:
    agent = ConAgenda("x")
    assert agent.sealed is False
    assert agent.seal().sealed is True
