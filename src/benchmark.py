"""Registro de tiempos de carga en resultados/benchmark_carga.csv."""

from pathlib import Path

import pandas as pd

LLAVE = ["estrategia", "base", "repeticion"]


def guardar_benchmark(filas: list[dict], ruta: Path) -> pd.DataFrame:
    """Agrega filas al CSV de benchmark sin borrar las de otras bases.

    Una fila nueva reemplaza a la existente con la misma (estrategia, base, repeticion);
    el resto del archivo se conserva. Las filas sin `repeticion` cuentan como la repetición 1.
    """
    nuevas = pd.DataFrame(filas)
    if "repeticion" not in nuevas:
        nuevas["repeticion"] = 1
    if ruta.exists():
        viejas = pd.read_csv(ruta)
        if "repeticion" not in viejas:
            viejas["repeticion"] = 1
        repetidas = viejas.set_index(LLAVE).index.isin(nuevas.set_index(LLAVE).index)
        nuevas = pd.concat([viejas[~repetidas], nuevas], ignore_index=True)
    nuevas["repeticion"] = nuevas["repeticion"].astype(int)
    nuevas.to_csv(ruta, index=False)
    return nuevas
