"""Pruebas mínimas: lógica directa y a través del protocolo MCP real."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import horario  # noqa: E402
from cliente import SERVIDOR, llamar  # noqa: E402
from mcp import ClientSession  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

FILAS = horario.cargar_horario()


def test_horario_existente():
    r = horario.consultar_horario(FILAS, "3A", "Lunes")
    assert "Inteligencia Artificial" in r and "LAB-4" in r
    assert "Sistemas Operativos" in r and "C-301" in r


def test_dia_sin_clases():
    assert horario.consultar_horario(FILAS, "1A", "Sábado") == "El grupo 1A no tiene clases el sábado."


def test_grupo_inexistente():
    r = horario.consultar_horario(FILAS, "9Z", "Lunes")
    assert r.startswith("El grupo «9Z» no existe")


def test_tildes_y_mayusculas():
    assert "Física" in horario.consultar_horario(FILAS, "1a", "miercoles")


def test_buscar_aula():
    assert "C-302" in horario.buscar_aula(FILAS, "compiladores", "3B")
    assert "no tiene la asignatura" in horario.buscar_aula(FILAS, "Química", "3B")


def test_por_mcp():
    async def run():
        async with stdio_client(SERVIDOR) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                nombres = {t.name for t in (await s.list_tools()).tools}
                assert {"consultar_horario", "buscar_aula"} <= nombres
                assert "LAB-4" in await llamar(s, "consultar_horario", {"grupo": "3A", "dia": "Lunes"})
                assert "no tiene clases" in await llamar(s, "consultar_horario", {"grupo": "1A", "dia": "Domingo"})
                assert "no existe" in await llamar(s, "consultar_horario", {"grupo": "9Z", "dia": "Lunes"})
    asyncio.run(run())
