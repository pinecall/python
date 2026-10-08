# Clínica Norte

Un agente entero, escrito como lo escribiría un cliente, con el layout del CLI único: el mismo
agente que el ejemplo de TypeScript (`agents/examples/clinica-norte`) y el de Ruby
(`ruby/examples/clinica_norte`), con la misma agenda, los mismos documentos y los mismos once
goldens, en Python. Su prompt es, byte a byte, el del ejemplo de Ruby para el estado de cada golden.

```
agents/clinica-norte/agent.py                    la clase: estado, fases, herramientas
agents/clinica-norte/agenda.py                   la agenda de la clínica, inventada y fija: lo que en producción sería su API
agents/clinica-norte/views/clinica-norte.jinja   la vista: el bloque `view`, como función del estado
docs/clinica-norte/*.md                          de lo que responde por turno: `pinecall docs push` los sube
test/clinica-norte/test_clinica.py               ring 0: sin red, sin clave, sin modelo, sin gateway
test/clinica-norte/goldens/                      ring 1: once conversaciones, más docs.json y memory.json
test/clinica-norte/memory/                       los casos de extracción que `pinecall remember` corre
```

La carpeta se llama como el slug del agente: `agents/clinica-norte/` es el agente `clinica-norte`.
Como un guion no se importa, el test carga la clase con `pinecall.testing.load`, igual que la
carga `pinecall start`: su carpeta como paquete, así que `agent.py` importa `from .agenda import …`.

```bash
# la suite del cliente, como la corre él (desde la raíz del paquete: make examples)
uv run pytest examples/clinica_norte

# el resto, con el CLI único (npm i -g pinecall), desde esta carpeta
pinecall prompt --state test/clinica-norte/goldens/no-reserva-antes-del-si.json
pinecall chat
pinecall test                    # ring 1: make ring1 desde la raíz del paquete
pinecall start
```

El CLI no carga la clase: arranca `python -m pinecall.serve` con el intérprete del propio proyecto,
`.venv/bin/python` ([../../docs/production.md](../../docs/production.md)). En este checkout ese
`.venv` es el del paquete: `make ring1` lo enlaza antes de correr los goldens.

Lo que la recepción se sabe de memoria — horarios, precios, qué necesita autorización — no está en
este repo: se escribe en la consola, Settings ▸ Knowledge (o `pinecall agent knowledge edit`), y el
modelo lo lee entero en cada llamada. La voz, el modelo, el saludo, el idioma, lo que la memoria
guarda (`pinecall memory policy`) y la base que busca por turno (`pinecall docs attach
clinica-norte --k 4`) son del mundo, no de la clase, y una clase que todavía los declara se
rechaza al importarse.

## Lo que este ejemplo enseña

- **Una fase mueve las herramientas.** `stage: Literal["identify", "choose", "book", "done"]` es un
  campo del estado como cualquier otro, y `stage=` en una tool es azúcar sobre `when=`.
- **Un hueco se reserva por su id, no por su hora.** Dos huecos a la misma hora con distinto
  profesional son indistinguibles en palabras; un id no se parece a otro, y uno que la agenda no
  ofreció se rechaza con la lista de los que sí.
- **`propose` y `book` son dos momentos distintos.** Sin el campo `proposed`, la vista no sabe si
  toca leerle la hora o reservarla, y un modelo obediente vuelve a leérsela en vez de reservar.
- **El día se resuelve a una fecha en el código.** «El martes» dicho un jueves es una fecha y sólo
  una; un día sin agenda vuelve vacío, y la vista lo nombra.
- **`confirm=` es lo que hace `book` irreversible en el cable.** La plataforma lee la frase después
  de la reserva, con lo que la tool devolvió.
- **`preview=2` corta lo que ve el modelo, no lo que guarda el estado.**
- **La agenda es un colaborador, no estado.** Un `cached_property`: cada llamada tiene la suya, y no
  aparece en ningún snapshot.
- **La vista es solo lo que escribe la clínica.** Lo que la memoria recuerda y lo que la base
  responde llegan al modelo como resultado de una herramienta, en el historial. La vista pregunta
  `remembers("médico habitual")` y decide una frase suya con la respuesta.
