"""Registro de tiempos de carga en resultados/benchmark_carga.csv."""

from pathlib import Path

import pandas as pd

LLAVE = ["estrategia", "base", "repeticion", "maquina"]
MAQUINA_POR_DEFECTO = "mac_m5"


def guardar_benchmark(filas: list[dict], ruta: Path) -> pd.DataFrame:
    """Agrega filas al CSV de benchmark sin borrar las de otras bases ni de otras máquinas.

    Una fila nueva reemplaza a la existente con la misma (estrategia, base, repeticion, maquina);
    el resto del archivo se conserva. Las filas sin `repeticion` cuentan como la repetición 1
    y las filas sin `maquina` como `MAQUINA_POR_DEFECTO` (la Mac donde se corrió primero).
    """
    nuevas = pd.DataFrame(filas)
    if "repeticion" not in nuevas:
        nuevas["repeticion"] = 1
    if "maquina" not in nuevas:
        nuevas["maquina"] = MAQUINA_POR_DEFECTO
    if ruta.exists():
        viejas = pd.read_csv(ruta)
        if "repeticion" not in viejas:
            viejas["repeticion"] = 1
        if "maquina" not in viejas:
            viejas["maquina"] = MAQUINA_POR_DEFECTO
        repetidas = viejas.set_index(LLAVE).index.isin(nuevas.set_index(LLAVE).index)
        nuevas = pd.concat([viejas[~repetidas], nuevas], ignore_index=True)
    nuevas["repeticion"] = nuevas["repeticion"].astype(int)
    nuevas.to_csv(ruta, index=False)
    return nuevas
