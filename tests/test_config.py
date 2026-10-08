"""What a class may say about itself, and the world's settings it is refused with their verb."""

import pytest

from pinecall import Agent, DeclarationRefused
from pinecall._config import THE_WORLDS, moved_to_the_world, slug_of


def test_a_class_that_names_its_voice_is_refused_with_the_verb_that_sets_it() -> None:
    def declared() -> type[Agent]:
        class Clinica(Agent):
            """Una clínica."""

            voice = "carolina"

        return Clinica

    with pytest.raises(DeclarationRefused) as refused:
        declared()

    assert str(refused.value) == (
        "`voice` is the world's now, not the class's: pinecall agent set --voice <name> "
        "— remove it from the class"
    )


@pytest.mark.parametrize("field", sorted(THE_WORLDS))
def test_every_setting_of_the_worlds_is_refused_written_or_only_annotated(field: str) -> None:
    for body in ({field: "x"}, {"__annotations__": {field: str}}):
        with pytest.raises(DeclarationRefused) as refused:
            type("Clinica", (Agent,), {"__doc__": "Una clínica.", **body})
        assert str(refused.value) == moved_to_the_world(field)
        assert THE_WORLDS[field] in str(refused.value)


def test_the_slug_is_the_class_name_in_kebab_case_unless_the_class_names_one() -> None:
    class ClinicaNorte(Agent):
        """Una clínica."""

    class HTTPDesk(Agent):
        """Un mostrador."""

    class Named(Agent):
        """Con nombre."""

        slug = "recepcion"

    assert [slug_of(ClinicaNorte), slug_of(HTTPDesk), slug_of(Named)] == [
        "clinica-norte",
        "http-desk",
        "recepcion",
    ]
