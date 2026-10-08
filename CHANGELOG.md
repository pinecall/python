# Changelog

## Unreleased

- `@pinecall.tool`: a method the model may call, its docstring the description and its `Args:`
  section each parameter's. The parameters' types are the method's annotations (a `Literal` is
  an enum, a pydantic model a nested object), and what the model sends is checked and converted
  before the method runs. `stage=`, `when=`, `confirm=`, `preview=`, `pii=` and `timeout=`; a
  tool may be a `def` or an `async def`. A tool with no docstring, a parameter a model cannot
  fill by name, `pii=` naming no parameter, or a stage the class does not declare is refused when
  the class is created. `Agent.tools()`, `visible_tools()` and `run_tool(name, arguments)`.
- `pinecall.Agent`: a class's annotated fields are its state, opened per call at the value written
  (each call gets its own copy of a list); `state(pii=True)` or `state(visibility=…)` says who may
  see one; a public `@property` is a derived field; `stage: Literal[...]` is the stage. Once
  sealed, only a tool or a hook may write a field (`UnauthoredWrite`), and every write is recorded
  with its author. A class that sets one of the world's settings (`voice`, `llm`, `language`…) is
  refused when it is created, with the `pinecall` verb that sets it.
- `pinecall.wire`: every frame, event and command the gateway speaks, the runtime's own pydantic
  models; a frame that does not fit raises `pinecall.WireError`, which says what did not fit.
- The package's frame: `import pinecall` gives `PinecallError`, the root of every error it will
  raise, and `__version__`. Typed (`py.typed`), Python 3.11 and up. Nothing to write an agent with yet.
