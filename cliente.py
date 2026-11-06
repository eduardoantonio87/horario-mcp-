"""Cliente MCP: arranca el servidor local, descubre sus herramientas y las ejecuta.

Uso:
  python cliente.py                         -> demo con las 3 pruebas mínimas
  python cliente.py consultar_horario grupo=3A dia=Lunes
  python cliente.py buscar_aula asignatura="Compiladores" grupo=3B
"""
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVIDOR = StdioServerParameters(
    command=sys.executable,
    args=[str(Path(__file__).parent / "servidor.py")],
)


async def llamar(sesion, nombre, argumentos):
    res = await sesion.call_tool(nombre, argumentos)
    return "\n".join(c.text for c in res.content if getattr(c, "type", "") == "text")


async def main(argv):
    async with stdio_client(SERVIDOR) as (leer, escribir):
        async with ClientSession(leer, escribir) as sesion:
            await sesion.initialize()

            herramientas = await sesion.list_tools()
            print("Herramientas descubiertas:")
            for h in herramientas.tools:
                print(f"  • {h.name}: {h.description}")
            recursos = await sesion.list_resources()
            print("Recursos:", ", ".join(str(r.uri) for r in recursos.resources))
            print()

            if argv:
                nombre = argv[0]
                args = dict(a.split("=", 1) for a in argv[1:])
                print(await llamar(sesion, nombre, args))
                return

            pruebas = [
                ("Horario existente: ¿qué clases tiene 3A el lunes y en qué aulas?",
                 "consultar_horario", {"grupo": "3A", "dia": "Lunes"}),
                ("Día sin clases: 1A el sábado",
                 "consultar_horario", {"grupo": "1A", "dia": "Sábado"}),
                ("Grupo inexistente: 9Z el lunes",
                 "consultar_horario", {"grupo": "9Z", "dia": "Lunes"}),
                ("Buscar aula: Compiladores del 3B",
                 "buscar_aula", {"asignatura": "Compiladores", "grupo": "3B"}),
            ]
            for titulo, nombre, args in pruebas:
                print(f"▶ {titulo}\n  {nombre}({args})")
                print("  " + (await llamar(sesion, nombre, args)).replace("\n", "\n  "))
                print()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
