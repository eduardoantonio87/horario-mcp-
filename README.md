# Consulta el horario de clases con MCP

Servidor MCP local con herramientas para consultar un horario de clases guardado en CSV, y un cliente MCP que las descubre y las ejecuta. Todo corre en la PC, sin plataformas externas.

## Estructura

```
horario.csv       Datos: asignatura, grupo, profesor, aula, dia, hora
horario.py        Lógica: lee el CSV y responde las consultas
servidor.py       Servidor MCP (stdio): expone herramientas y un recurso
cliente.py        Cliente MCP: descubre las herramientas y las llama
test_horario.py   Pruebas mínimas (lógica y protocolo MCP)
```

## Herramientas y recurso MCP

| Tipo | Nombre | Qué hace |
|---|---|---|
| Herramienta | `consultar_horario(grupo, dia)` | Clases de un grupo en un día, con hora, aula y profesor |
| Herramienta | `buscar_aula(asignatura, grupo)` | Aula, día y hora de una asignatura para un grupo |
| Herramienta | `listar_grupos()` | Grupos que existen en el horario |
| Recurso | `horario://clases.csv` | El CSV completo, solo lectura |

Las consultas no distinguen mayúsculas ni tildes (`miercoles` = `Miércoles`). Si no hay clases o el grupo no existe, se devuelve un mensaje claro en vez de un error.

## Cómo ejecutarlo

Necesitas Python 3.10 o superior.

```bash
git clone <url-de-este-repositorio>
cd horario-mcp-

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

Demo con las pruebas mínimas (el cliente arranca el servidor solo):

```bash
python cliente.py
```

Una consulta concreta:

```bash
python cliente.py consultar_horario grupo=3A dia=Lunes
python cliente.py buscar_aula asignatura="Compiladores" grupo=3B
```

Pruebas automáticas:

```bash
python -m pytest -q
```

Para inspeccionarlo con el MCP Inspector oficial (requiere Node.js): `npx @modelcontextprotocol/inspector python servidor.py`

## Ejemplo

Pregunta: «¿Qué clases tiene el grupo de tercer año el lunes y en qué aulas?»
Llamada: `consultar_horario(grupo="3A", dia="Lunes")`

```
Clases del grupo 3A el lunes:
- 08:00-09:30  Inteligencia Artificial  (aula LAB-4, prof. Marta Cruz)
- 09:45-11:15  Ingeniería de Software  (aula C-301, prof. Luis Ortega)
- 11:30-13:00  Sistemas Operativos  (aula LAB-2, prof. Jorge Rivas)
```

## Prueba mínima

| Caso | Llamada | Resultado |
|---|---|---|
| Horario existente | `consultar_horario("3A", "Lunes")` | 3 clases con aulas LAB-4, C-301 y LAB-2 |
| Día sin clases | `consultar_horario("1A", "Sábado")` | `El grupo 1A no tiene clases el sábado.` |
| Grupo inexistente | `consultar_horario("9Z", "Lunes")` | `El grupo «9Z» no existe. Grupos disponibles: 1A, 2A, 3A, 3B.` |

## Investigación breve: herramienta frente a respuesta sin consultar

**Con herramienta (MCP).** El modelo no sabe el horario; decide llamar a `consultar_horario` con los parámetros adecuados, el servidor lee el CSV en ese momento y devuelve el dato exacto. La respuesta se basa en la fuente real: si el CSV cambia, la respuesta cambia; si el grupo no existe, el servidor lo dice. Es verificable (la llamada y su resultado quedan registrados) y el modelo solo redacta a partir de datos concretos.

**Sin consultar.** El modelo responde solo con lo que aprendió en su entrenamiento y con lo que haya en la conversación. No conoce este horario, que es privado y cambia, así que tiene que adivinar: puede inventar aulas, horas o profesores con total seguridad (alucinación), no detecta que un grupo no existe y no se entera de cambios. Además no hay forma de comprobar de dónde sacó la respuesta.

**En resumen:** la herramienta convierte la pregunta en una consulta a datos reales y actuales; sin ella, el modelo genera texto plausible pero no fiable. MCP estandariza esa conexión: el cliente descubre qué herramientas hay (`list_tools`) y las ejecuta (`call_tool`), y el servidor puede además exponer recursos legibles como el CSV.
