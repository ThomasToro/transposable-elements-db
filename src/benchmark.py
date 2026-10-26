"""Registro de tiempos de carga en resultados/benchmark_carga.csv."""

from pathlib import Path

import pandas as pd


def guardar_benchmark(filas: list[dict], ruta: Path) -> pd.DataFrame:
    """Agrega filas al CSV de benchmark sin borrar las de otras bases.

    Una fila nueva reemplaza a la existente con la misma (estrategia, base);
    el resto del archivo se conserva.
    """
    nuevas = pd.DataFrame(filas)
    if ruta.exists():
        viejas = pd.read_csv(ruta)
        llave = viejas.set_index(["estrategia", "base"]).index
        repetidas = llave.isin(nuevas.set_index(["estrategia", "base"]).index)
        nuevas = pd.concat([viejas[~repetidas], nuevas], ignore_index=True)
    nuevas.to_csv(ruta, index=False)
    return nuevas
