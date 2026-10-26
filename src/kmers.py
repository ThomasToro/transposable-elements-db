"""Cálculo de conteos de k-mers (funciones puras, sin MongoDB)."""

from itertools import product

import numpy as np

K_RANGE = range(1, 7)
INVALIDO = 4

# A, C, G, T -> 0..3; cualquier otro byte (N, IUPAC) -> INVALIDO
_CODIGO = np.full(256, INVALIDO, dtype=np.uint8)
for _i, _b in enumerate(b"ACGT"):
    _CODIGO[_b] = _i

# Nombre de cada índice en base 4, por k: _NOMBRES[k][i] == "AC…"
_NOMBRES = {k: ["".join(p) for p in product("ACGT", repeat=k)] for k in K_RANGE}


def _codificar(seq: str) -> np.ndarray:
    return _CODIGO[np.frombuffer(seq.upper().encode("ascii", "replace"), dtype=np.uint8)]


def _contar(cod: np.ndarray, k: int) -> dict:
    n = len(cod) - k + 1
    if n <= 0:
        return {"valid_windows": 0, "counts": {}}
    # Una ventana es válida si no contiene ningún INVALIDO: suma acumulada de inválidos
    malos = np.concatenate(([0], np.cumsum(cod == INVALIDO)))
    validas = (malos[k:] - malos[:n]) == 0
    # Índice en base 4 de cada ventana (los inválidos se enmascaran después)
    base = np.minimum(cod, 3).astype(np.int64)
    idx = np.zeros(n, dtype=np.int64)
    for j in range(k):
        idx = idx * 4 + base[j:j + n]
    conteo = np.bincount(idx[validas], minlength=4 ** k)
    presentes = np.flatnonzero(conteo)
    nombres = _NOMBRES[k]
    return {
        "valid_windows": int(validas.sum()),
        "counts": {nombres[i]: int(conteo[i]) for i in presentes},
    }


def kmer_counts(seq: str, k: int) -> dict:
    """Conteos de k-mers con ventana deslizante de 1.

    Descarta toda ventana con caracteres distintos de A, C, G, T.
    Devuelve {"valid_windows": int, "counts": dict} como define MODELO.md.
    """
    return _contar(_codificar(seq), k)


def all_kmer_counts(seq: str, ks=K_RANGE) -> dict:
    """Conteos para cada k de ks: {k: {"valid_windows", "counts"}}."""
    cod = _codificar(seq)
    return {k: _contar(cod, k) for k in ks}
