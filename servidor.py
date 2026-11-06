"""Servidor MCP local (transporte stdio) que expone el horario de clases.

Herramientas:  consultar_horario(grupo, dia), buscar_aula(asignatura, grupo), listar_grupos()
Recurso:       horario://clases.csv  (el CSV completo, legible)
"""
from mcp.server.fastmcp import FastMCP

import horario

mcp = FastMCP("horario-clases")


@mcp.tool()
def consultar_horario(grupo: str, dia: str) -> str:
    """Devuelve las clases de un grupo (p. ej. '3A') en un día (p. ej. 'Lunes'), con hora, aula y profesor."""
    return horario.consultar_horario(horario.cargar_horario(), grupo, dia)


@mcp.tool()
def buscar_aula(asignatura: str, grupo: str) -> str:
    """Indica en qué aula(s), día y hora recibe un grupo una asignatura."""
    return horario.buscar_aula(horario.cargar_horario(), asignatura, grupo)


@mcp.tool()
def listar_grupos() -> str:
    """Lista los grupos que existen en el horario."""
    return "Grupos: " + ", ".join(sorted({f["grupo"] for f in horario.cargar_horario()}))


@mcp.resource("horario://clases.csv", mime_type="text/csv")
def horario_csv() -> str:
    """El archivo CSV completo del horario."""
    return horario.RUTA_CSV.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()  # stdio
