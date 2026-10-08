# Architecture — `pinecall`, the Python package a tenant writes an agent in

What this repository is, file by file, what each piece corresponds to in the TypeScript package
and in the Ruby gem it is brought over from, and where it meets the runtime (`pinecall/runtime`),
whose wire it speaks.

**The thesis.** An agent is an object. Fields are state. Methods are capabilities. Docstrings are
prompts. Types are contracts. The prompt is `render(state)`. Tools are the only thing that changes
state. The log is the truth.

---

## 1. Four repositories, one product

| repository | language | what it owns |
|---|---|---|
| `pinecall/runtime` | Python, on livekit-agents | the wire and its golden log; the real time: LiveKit rooms and SIP, STT/LLM/TTS, the gateway's doors, the log, the judges |
| `pinecall/agents` | TypeScript, Node ≥ 24 | the same class, for a team that writes TypeScript (`@pinecall/agents`) |
| `pinecall/ruby` | Ruby ≥ 3.2 | the same class, for a team that writes Ruby |
| `pinecall/cli` | TypeScript, Node ≥ 24 | the one `pinecall` CLI, for every language: it starts this package's serve entry |
| **`pinecall/python`** (this one) | Python ≥ 3.11 | the same class, for a team that writes Python |

The line between this package and the runtime is a **socket**. This package never imports the
runtime, never speaks HTTP to a vendor, never sees audio, and holds no key of its own beyond the
one the person typed.

## 2. The tree

```
src/pinecall/
  __init__.py                the door: what a stranger who types `import pinecall` may reach
  _version.py                the version, written once; 0.0.0 until the human names a number
  errors.py                  one root, `PinecallError`
  py.typed                   the package is typed (PEP 561)
tests/                       mirrors src/ one to one
  test_init.py               the door, pinned by name
  rules/test_the_tree.py     the ceiling, the opening line of every module, the mirror
```

## 3. What came from where

One row per piece, against the TypeScript package and the Ruby gem. Every row is a decision, not a
translation; the rows land with the code they describe.

| in `pinecall/agents` (TS) | in `pinecall/ruby` | here (Python) | why it is different |
|---|---|---|---|
| `test/index.test.ts` pins the exports by name | `sig/pinecall.rbs` and `rake rbs` | `__init__.py` re-exports `X as X` with `__all__`, `tests/test_init.py` pins the list | Adding to the surface means editing the pin on purpose. pyright strict reads `X as X` as a re-export. |
| one error root | `Pinecall::Error` | `PinecallError`, named by the door (`__module__ == "pinecall"`) | A traceback names what a person imports, not the private module that defined it. |

## 4. Packaging

- **A library, no executable.** The verbs are the one `pinecall` CLI's (npm); it starts
  `python -m pinecall.serve`.
- **PyPI `pinecall`, import `pinecall`.** The runtime's distribution is `pinecall-runtime`; the two
  are never installed in one environment.
- **Python ≥ 3.11**, checked on 3.11, 3.12 and 3.13. A tenant's server is not ours to upgrade.
- **The version is written once**, `src/pinecall/_version.py`, and hatch reads it; a `v*` tag that
  says another number is refused before anything is built (`release.yml`'s guard).
- **Typed:** `py.typed` ships in the wheel, and the release checks it is there.
- **`make check`** is ruff (every rule, and the format), pyright strict, deptry and the suite.
