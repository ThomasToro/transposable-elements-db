"""Normalización de nombres para cruzar el CSV de especies con el FASTA."""

import re

_ESPACIOS = re.compile(r"\s+")


def normalize_species(nombre: str) -> str:
    """Devuelve la llave de cruce de un nombre de especie.

    Elimina los puntos, quita espacios al inicio y al final, reduce cualquier
    secuencia de espacios (incluidos tabs) a uno solo y pasa todo a minúsculas.

    Los puntos se eliminan porque el FASTA abrevia con punto (``subsp.``, ``sp.``)
    y el CSV sin él (``subsp``, ``sp``).

    >>> normalize_species("  Beta   vulgaris subsp. vulgaris ")
    'beta vulgaris subsp vulgaris'

    Solo sirve para comparar: en la base se guarda el nombre original (con strip).
    """
    return _ESPACIOS.sub(" ", nombre.replace(".", "").strip()).lower()
