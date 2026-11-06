"""Lógica pura del horario: lectura del CSV y consultas (sin dependencias de MCP)."""
import csv
import unicodedata
from pathlib import Path

RUTA_CSV = Path(__file__).parent / "horario.csv"
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para comparar 'miercoles' con 'Miércoles'."""
    texto = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def cargar_horario(ruta: Path = RUTA_CSV) -> list[dict]:
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _grupos(filas):
    return sorted({f["grupo"] for f in filas})


def _dia_valido(dia: str):
    for d in DIAS:
        if normalizar(d) == normalizar(dia):
            return d
    return None


def consultar_horario(filas: list[dict], grupo: str, dia: str) -> str:
    grupos = _grupos(filas)
    g = next((x for x in grupos if normalizar(x) == normalizar(grupo)), None)
    if g is None:
        return f"El grupo «{grupo}» no existe. Grupos disponibles: {', '.join(grupos)}."
    d = _dia_valido(dia)
    if d is None:
        return f"«{dia}» no es un día válido. Usa: {', '.join(DIAS)}."
    clases = [f for f in filas if f["grupo"] == g and normalizar(f["dia"]) == normalizar(d)]
    if not clases:
        return f"El grupo {g} no tiene clases el {d.lower()}."
    clases.sort(key=lambda f: f["hora"])
    lineas = [f"Clases del grupo {g} el {d.lower()}:"]
    for f in clases:
        lineas.append(f"- {f['hora']}  {f['asignatura']}  (aula {f['aula']}, prof. {f['profesor']})")
    return "\n".join(lineas)


def buscar_aula(filas: list[dict], asignatura: str, grupo: str) -> str:
    grupos = _grupos(filas)
    g = next((x for x in grupos if normalizar(x) == normalizar(grupo)), None)
    if g is None:
        return f"El grupo «{grupo}» no existe. Grupos disponibles: {', '.join(grupos)}."
    clases = [f for f in filas if f["grupo"] == g and normalizar(f["asignatura"]) == normalizar(asignatura)]
    if not clases:
        asign = sorted({f["asignatura"] for f in filas if f["grupo"] == g})
        return (f"El grupo {g} no tiene la asignatura «{asignatura}». "
                f"Sus asignaturas son: {', '.join(asign)}.")
    orden = {d: i for i, d in enumerate(DIAS)}
    clases.sort(key=lambda f: (orden.get(f["dia"], 99), f["hora"]))
    lineas = [f"{clases[0]['asignatura']} del grupo {g}:"]
    for f in clases:
        lineas.append(f"- {f['dia']} {f['hora']}: aula {f['aula']} (prof. {f['profesor']})")
    return "\n".join(lineas)
