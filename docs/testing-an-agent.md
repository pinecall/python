# Testing an agent

Ring 0 is the ring your own suite lives in: no network, no key, no model, no gateway. It runs on
every commit, in a second, and it is where nearly every mistake is caught.

```python
from pathlib import Path

from pinecall.testing import Gateway, load

# A folder named by a slug cannot be imported: the class is loaded as `pinecall start` loads it,
# its folder a package, so `agent.py` imports what sits beside it with `from .agenda import …`.
ClinicaNorte = load(Path(__file__).parents[2] / "agents" / "clinica-norte" / "agent.py")


def test_una_paciente_de_la_ficha_no_tiene_que_decir_su_nombre_otra_vez() -> None:
    with Gateway() as pc:
        pc.mount(ClinicaNorte)
        call = pc.call_started(from_="+34600123456")

        assert "Hablas con Marta Ruiz" in call.prompt
        assert call.tools == ["free_slots"]
```

`pinecall.testing.Gateway` is a gateway that is not there. It answers the declarations, keeps
every command the agent sent, and lets the test say what happened next; each step returns once the
agent has finished answering it. It needs no plugin: a plain `def test_…` drives it, and the
`with` block closes the loop it runs on.

## Driving a call

| you write | what happens |
|---|---|
| `pc.call_started(from_=, channel=, medium=, id_=, state=)` | a call opens, `on_call` runs, then `state=` (what `call.started` carries when a golden or a persona opened it) is written over the hook's, and the first prompt goes out. Returns the handle |
| `call.tool("free_slots", day="martes")` | the model calls a tool. Returns the `tool.result` the agent sent back: `output`, or `error` |
| `call.said("el martes me viene bien")` | the caller said something |
| `call.fact("agenda.changed", {"slots": []})` | a fact from your backend; `source="participant"` for a browser |
| `call.ended()` | the call is over, `on_end` runs |
| `pc.call_attached(state, id_=)` | a call handed over mid-conversation: no `on_call`, the state the gateway kept, the whole prompt sent |
| `pc.finds(Found(path, heading, text), …)` | what every search answers with; `pc.searched` is what was asked, `(call, query, k)` each |

## Asking what the agent said

| you read | what it is |
|---|---|
| `call.prompt` | the `view` block as the agent last sent it: the last thing the model reads |
| `call.block("identity")` | any of the four blocks as the agent last sent it, by name; `""` until it had something to say |
| `call.tools` | the tools the model may call right now, by name |
| `call.state` | the state as the agent last sent it |
| `call.commands` | everything sent on this call, in order |
| `call.last("call.log", name="cita")` | the last command of one type whose fields match |
| `mounted.instance_of(call.id)` | the instance itself, for an assertion about a field |
| `pc.errors` | what failed with nobody waiting for it — an empty list is an assertion worth making |

## What is worth a test

The things a prompt makes true, not the things a method returns:

```python
def test_el_telefono_pide_ofrecer_dos_horas() -> None:
    with Gateway() as pc:
        pc.mount(ClinicaNorte)
        call = pc.call_started(from_="+34600123456", channel="phone")
        call.tool("free_slots", day="el martes", specialty="medicina de familia")

        assert "Ofrece como máximo dos" in call.prompt


def test_una_hora_que_nadie_ofrecio_se_rechaza_en_vez_de_reservarse() -> None:
    with Gateway() as pc:
        pc.mount(ClinicaNorte)
        call = pc.call_started(from_="+34600123456")
        call.tool("free_slots", day="el martes", specialty="medicina de familia")

        assert "no es una de las horas" in str(call.tool("propose", slot="el domingo")["error"])
```

A tool that raises is not a broken test: the model is waiting for an answer and reads the message
as the tool's own result, so `call.tool(...)` gives you back `{"error": "…"}` and the call carries
on. That is what you assert on.

## Without mounting anything

The prompt is a function of the state, so most assertions need no gateway at all:

```python
from pinecall import CallLine, CallWorld, render

agent = ClinicaNorte().seal()
agent.serving(CallWorld(CallLine(id="CA_1", channel="phone", today="2026-09-17")))
agent.start_in({"stage": "book", "slots": [hueco]})

assert "el martes a las diez" in render(agent)["view"]
assert agent.run_tool("propose", {"slot": "s-1"}) == hueco
```

`start_in` writes the fields a case names over the ones the class gave itself; `restore` means
something stronger, a whole state, so a field it leaves out is cleared. `run_tool` runs a tool as
a call does — its arguments checked and converted, its writes authored, its list cut to its
`preview` — and runs an `async def` tool to its end.

## The rings above

The verbs are the one `pinecall` CLI's (npm), the same for a Python project as for a TypeScript or
a Ruby one, in the same layout: `agents/<slug>/agent.py`, `test/<slug>/goldens/`,
`test/<slug>/memory/`, `docs/<slug>/`. For the ones that need the class, the CLI starts this
package's serve entry, `python -m pinecall.serve`, with the project's own interpreter.

| ring | what it asks | how |
|---|---|---|
| 1 | does the agent hold its goldens? | `pinecall test` — the goldens under `test/<slug>/goldens/`, each call served by this package's entry |
| 2 | does it hold on a real line? | `pinecall test --voice` · `pinecall simulate --voice` |
| 3 | what does one real call score? | `pinecall eval <call-id>` |
| 4 | what did every call score? | `call.score`, written by the runtime at hang-up |

The index and memory have goldens of their own — whether retrieval returns the chunk a question
needs (`pinecall docs eval`), whether recall brings back the fact a question needs
(`pinecall memory eval`), and what the hang-up's one model call writes, replaces and must never
keep (`pinecall remember`, the cases in `test/<slug>/memory/`). They are files beside the
project, run by the CLI and the same for every language: [Testing knowledge and memory](https://docs.pinecall.io/guides/testing-knowledge-and-memory/).
