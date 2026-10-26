"""Cálculo de conteos de k-mers (funciones puras, sin MongoDB)."""

import re
from collections import Counter

K_RANGE = range(1, 7)
_VALID_RUN = re.compile(r"[ACGT]+")


def kmer_counts(seq: str, k: int) -> dict:
    """Conteos de k-mers con ventana deslizante de 1.

    Descarta toda ventana con caracteres distintos de A, C, G, T.
    Devuelve {"valid_windows": int, "counts": dict} como define MODELO.md.
    """
    counts = Counter()
    # Solo los tramos continuos de ACGT generan ventanas válidas.
    for run in _VALID_RUN.findall(seq.upper()):
        counts.update(run[i:i + k] for i in range(len(run) - k + 1))
    return {"valid_windows": sum(counts.values()), "counts": dict(counts)}


def all_kmer_counts(seq: str, ks=K_RANGE) -> dict:
    """Conteos para cada k de ks: {k: {"valid_windows", "counts"}}."""
    seq = seq.upper()
    return {k: kmer_counts(seq, k) for k in ks}
