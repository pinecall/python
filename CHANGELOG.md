# Changelog

## Unreleased

- `pinecall.wire`: every frame, event and command the gateway speaks, the runtime's own pydantic
  models; a frame that does not fit raises `pinecall.WireError`, which says what did not fit.
- The package's frame: `import pinecall` gives `PinecallError`, the root of every error it will
  raise, and `__version__`. Typed (`py.typed`), Python 3.11 and up. Nothing to write an agent with yet.
