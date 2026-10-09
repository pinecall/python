# Writing an agent

An agent is one Python class. Everything the model can see about it comes from four places: the
class's docstring, what the class declares, the docstrings of its tools, and the view.

```python
from typing import Literal

from pinecall import Agent, state, tool


class ClinicaNorte(Agent):
    """You are the front desk of Clínica Norte. Formal, short sentences.
    Everything you say is read aloud: no lists, no markdown."""
```

That docstring is the `identity` block of the prompt — the first of the static blocks, which never
change during a call and are what a provider caches. Write it as instructions to a person, not as
documentation. It reaches the model on one line, its blank lines dropped.

## Config: what the agent *is*

Written on the class, unannotated or as a `ClassVar`, because it is not something the agent
remembers. It never changes during a call and no view renders it.

| written | what it does |
|---|---|
| `channel_rules = False` | leaves out the `<channel>` part of the prompt: how to write for a voice, a website's chat, WhatsApp |
| `slug = "front-desk"` | the name the agent registers as; left out, the class's name in kebab-case (`ClinicaNorte` → `clinica-norte`) |
| `accepts = {"slot.released": ["app"]}` | the outside events the agent takes, and from whom: `app` is your backend, `participant` a browser in the call |

### The world's, not the class's

Everything the agent **runs on** is the world's: set per world, versioned, with who set it and
why, and changed without a deploy — by `pinecall agent set`, the console's Settings tab, or the
verb the table names. A class that still declares one of these, written or only annotated, is
refused when the class is created — on the file's own import, before a prompt is printed or a
gateway is knocked at — with the verb that sets it now:

```
`voice` is the world's now, not the class's: pinecall agent set --voice <name> — remove it from the class
```

| field | what it is | where it is set |
|---|---|---|
| `voice` | a voice **by name** — the platform resolves it to a vendor and an id | `pinecall agent set --voice` |
| `llm` | `haiku`, `sonnet`, `opus`, or `vendor/model` | `pinecall agent set --llm` |
| `stt` | the ears: `deepgram` (Flux), `soniox`, or `vendor/model` | `pinecall agent set --stt` |
| `language` | the language the call is in | `pinecall agent set --language` |
| `greeting` | how the call opens: the words, or what the model reads before finding its own | `pinecall agent set --greeting '…'` · `--reply '…'` |
| `hangup` | whether the model may end the call itself, and when, in your words | `pinecall agent set --hangup '…'` |
| `says` | how a word the voice would misread is said: `DKV` → `de ka uve` | `pinecall lexicon add <word> --say '…'` |
| `hears` | the words the ears must know: names, brands, the doctor's surname | `pinecall lexicon hear <word> …` |
| `memory` | what to remember about a caller across calls, and what never to | `pinecall memory policy --remember '…' --forget '…'` |
| `record` | whether the call is recorded | `pinecall agent set --record on\|off` |
| `knowledge` | what the agent knows by heart: a page of Markdown, read whole on every call | `pinecall agent knowledge edit` |
| `docs` | the bases the agent searches per turn | `pinecall docs push`, then `pinecall docs attach <base>` |

**Neither a fact the agent remembers nor a chunk of a base ever reaches the prompt.** Both arrive
as a tool result, in the history, where a model reads them as information rather than as an
instruction. A tool that searches calls `self.knowledge.search(…)`; the class says nothing about
it, and the package reads it off the class's file when the agent registers, so a world with no
base attached is refused then rather than at the first turn.

## State: what it remembers

Every annotated attribute whose name does not start with `_` and that is not a `ClassVar` is a
state field. Its value is where every call opens; a list or a dict is copied, so no two calls ever
share one.

```python
class ClinicaNorte(Agent):
    stage: Literal["identify", "choose", "book", "done"] = "identify"
    patient: dict | None = state(pii=True)
    slots: list[dict] = []
    proposed: dict | None = None

    @property
    def identified(self) -> bool:  # derived: in every snapshot, assigned by nobody
        return self.patient is not None
```

- **`stage`** is a `Literal` of the values it may hold, opening at the one written (the first, if
  none is). A tool's `stage=` is checked against it, and setting it to anything else raises
  `NotAStage` — pyright says so before the code runs.
- **`state(...)`** is for a field that also says who may see it: `state(pii=True)`, or
  `state(default, visibility="public")`. Left out, the wire's default applies (`tenant`).
- **A public `@property` is a derived field.** A `cached_property`, a method or a `_name` is a
  collaborator — the agenda, a client — and never state.
- A subclass's own `__init__` needs no `super().__init__()`: the state opens on its first use.

**Tools are the only writers.** Once the agent is sealed — every call seals its instance — a write
anywhere but in a tool or a hook raises `UnauthoredWrite`:

```
state field patient was assigned outside a tool and outside a lifecycle hook; tools are the only writers of state
```

Every write is recorded with its author, the tool's own name, carried by a `ContextVar`: two calls
served at the same moment never read each other's. `agent.changes()` is the record;
`agent.collapse("…")` replaces it with one sentence; `agent.log(name, data)` writes a line of your
own into the call's log.

## Tools: what the model may do

```python
class ClinicaNorte(Agent):
    @tool(stage="identify", pii=("name", "phone"))
    def find_patient(self, name: str, phone: str) -> dict | None:
        """Finds the patient's file by their full name and phone.

        Call it only once the patient has given you both.

        Args:
            name: the full name, as they said it
            phone: the phone number, as they said it
        """
        self.patient = self.agenda.find(name, phone)
        if self.patient:
            self.stage = "choose"
        return self.patient
```

The docstring, up to its first section, is what the model reads to choose the tool; the `Args:`
section is what it reads of each parameter; the annotations are the schema it fills, and what it
sends is checked and converted against them before the method runs: a `Literal` is an enum, a
pydantic model a nested object, `"3"` for an `int` is `3`. A parameter with no annotation is
`str` — what a person on the phone says.

| option | what it does |
|---|---|
| `stage=` | visible while the state is in this stage, or one of these: `stage=("choose", "book")` |
| `when=` | a question asked of the agent on every change: `when=lambda self: bool(self.slots)` |
| `confirm=` | the read-back said before running. **This is what makes a tool irreversible on the wire**; `{{result.x}}` names a field of what it returns |
| `preview=` | how many rows of a list the *model* sees. The state keeps every row |
| `pii=` | the parameters that carry personal data, masked in the log |
| `timeout=` | how many seconds the platform waits for this method |

A tool may be a `def` or an `async def`. In a call, an `async def` runs on the event loop and a
`def` on a thread of its own, so a blocking call to your systems never holds the socket; both
write as the tool. In a test, `agent.run_tool("find_patient", {"name": "Ana", "phone": "600…"})`
runs either to its end, as a call would.

## The hooks

```python
class ClinicaNorte(Agent):
    def on_call(self, call: CallWorld) -> None:  # a call started; writes here are the hook's
        self.patient = self.agenda.by_phone(call.from_ or "")
        if self.patient:
            self.stage = "choose"

    def on_end(self, call: CallWorld) -> None:  # a line logged here still lands
        self.log("outcome", {"stage": self.stage})

    def on_event(
        self, name: str, data: JsonObject, meta: EventMeta
    ) -> None: ...  # an accepted outside fact
    def on_memory(self, ops: list[MemoryOp], call: CallWorld) -> None: ...  # memory read or written
```

Each may be a `def` or an `async def`. `on_call` runs before the first prompt goes out, so the
model never reads a state the call was not in; the state a golden or a persona opens the call in
is applied after it, so the hook never overwrites it. An outside fact reaches `on_event` only if
the class `accepts` the pair — an event declared from `app` that arrives from a browser is
somebody else's event with your name on it, and the hook never sees it.

## The call

Inside a tool or a hook, `self.call` is the live call; outside one it says so rather than being
`None`.

```python
self.say("One moment, let me check.")  # an Answer: True once the turn lands, False after 30 s
self.reply("Tell them it is booked.")  # the model speaks, guided by words nobody hears
self.call.send("cart", {"total": 42})  # a payload to the browsers in the room
self.call.participant(identity).mute()  # and .remove()
self.call.invite("+34910000001")  # a phone leg; invite(identity, "participant") for a seat
self.call.transfer("+34910000002")  # an Answer: a Transferred, ok=False if they are still here
self.call.attention("wants to talk to a person", wait_s=60)  # an Attended: who took the line
self.call.hold()  # and unhold()
self.call.dtmf("1#")
self.call.claim("4821")  # the page showing 4821 follows this call; call.claimed says so
self.call.callback("+34600000001", when="tomorrow afternoon", note="a quote")
self.call.opt_out("does not want more calls")  # their number joins the do-not-call list
self.call.hangup("done")
self.knowledge.search("summer opening hours", k=3)  # an Answer: the chunks, searched for this call
```

**A verb that waits answers with an `Answer`.** In an `async def` tool, `await` it; in a `def`
tool, which runs on a thread of its own, `.result()` waits for it there — or leave it, and the
command still goes. It is settled by the entry that says how it went, by its ceiling, or by the
call ending first (`ok=False`, `the call ended before it was answered`).

There is no LiveKit here and no escape hatch to it: a need the room cannot express is a new
command with a name.

## The panel beside a conversation: `@panel`

The console draws a pane beside every thread in **Calls**. Without a panel it is what the console
itself knows — how many conversations there have been with this person, what they came in by, how
long the agent spent on the line with them. A class that declares a panel has **its own drawn over
that**, and that is where the business's data goes: the customer's file, their orders, the balance.

```python
from pinecall import Agent, Drawing, Who, panel


class ClinicaNorte(Agent):
    @panel("Customer")
    def file(self, who: Who, draw: Drawing) -> None:
        client = self.crm.find(who.contact)
        if client is None:
            with draw.panel("Not on file"):
                draw.text("Not in the CRM.")
            return
        with draw.panel(client.name):
            with draw.rows():
                draw.row("Since", client.since)
                draw.row("Area", client.area)
            draw.stat("Jobs", len(client.jobs))
            draw.table(["date", "job", "amount"], client.jobs)
            draw.badge(
                "owes" if client.debt else "paid up", tone="warn" if client.debt else "good"
            )
```

It is the TypeScript package's `@view`, and what reaches the console is the same: a tree of the
closed catalogue — `panel`, `rows`, `row`, `stat`, `table`, `badge`, `text` — drawn by the console's
own parts, in the theme the person reading chose; nothing a tenant writes reaches the page's
styling, its scripts or its key. `who` is the conversation — `agent`, `contact`, `call` — and nothing
else: the panel is read beside threads that ended weeks ago, so it fetches what it shows, on an
instance of its own, never from a call's state. It may be an `async def`. A table's row is a
sequence in the columns' order or a mapping keyed by them; a number is written whole when it is
whole, and `None` or a boolean draws nothing. One per class, and a subclass does not inherit it.

## What is refused when the class is created

Every one of these raises `DeclarationRefused` on the file's import — never in the middle of a
call, and never as a refusal from a gateway:

| refused | the sentence |
|---|---|
| a tool with no docstring | `without a docstring no model can choose it` |
| `def book(self, *chosen)`, `**kwargs`, or a positional-only parameter | `a model fills a JSON object by name, so every parameter is one it can name` |
| `pii=("dni",)` on a tool with no `dni` | `pii names parameters the tool has; unknown: dni` |
| `stage="pay"` where the `Literal` has no `"pay"` | `pay is not one of this agent's stages (identify, book)` |
| `stage=` on a class with no `stage` | `…declares none; add stage: Literal["identify", "book"] to the class` |
| `stage: str` | `stage names the values it may hold: stage: Literal["identify", "book"]` |
| a field named like the agent's own (`snapshot`, `log`, `call`…) | `` `snapshot` is a name the agent itself uses; call the field otherwise`` |
| a tool named like the agent's own method | `a tool named so would hide the agent's own log` |
| an `accepts` sender that is not `app` or `participant` | `'browser' sends nothing; an event comes from app or participant` |
| `state(pii=True, visibility="public")` | `a field is pii or public, not both` |
| two `@panel` methods | `declares two panels (Customer and Orders); a class draws one panel` |
| a `@panel` method that does not take `(self, who, draw)` | `a panel draws with (self, who, draw)` |
| `voice`, `llm`, `stt`, `language`, `greeting`, `hangup`, `says`, `hears`, `memory`, `record`, `knowledge`, `docs` | `` `<field>` is the world's now, not the class's: <verb> — remove it from the class`` |
