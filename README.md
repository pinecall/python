# pinecall

Write a [Pinecall](https://pinecall.io) voice or chat agent as a Python class: its fields are the
state, its tools are the model's verbs, its docstrings are the prompt. The one `pinecall` CLI
serves it.

**Not released yet.** The TypeScript package (`@pinecall/agents`) and the Ruby gem are what a team
writes an agent in today; this package is being built to the same contract.

## Developing

```bash
uv sync
make check
```

How the package is built, file by file, is [ARCHITECTURE.md](ARCHITECTURE.md). A whole agent,
written the way a customer writes one, is [examples/clinica_norte](examples/clinica_norte).

## License

Apache-2.0.
