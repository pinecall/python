# Docs

The pages a person writing an agent reads. The map of the package itself — every file, and what
each piece corresponds to in the TypeScript package and the Ruby gem — is
[../ARCHITECTURE.md](../ARCHITECTURE.md).

| page | what it answers |
|---|---|
| [writing-an-agent.md](writing-an-agent.md) | the class: config, state, the stage, tools, the events it accepts, and what is refused when it is created |
| [the-view.md](the-view.md) | the prompt as named blocks in two regions, and the Jinja template that renders the view |
| [testing-an-agent.md](testing-an-agent.md) | ring 0 with `pinecall.testing`, a suite with no network, no key and no model, and the rings above |
| [production.md](production.md) | how a server runs the agent: `pinecall start --prod`, or `pinecall.hold` in your own process |
