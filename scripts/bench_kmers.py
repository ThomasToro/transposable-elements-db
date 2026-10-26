"""Benchmark de src/kmers.py: 1 proceso frente a multiprocessing.

Uso (desde la raíz del repo):
    conda activate panteon
    python scripts/bench_kmers.py

Lee las primeras 2.000 secuencias de data/PanTEon_Database_v1.6.1.fasta, calcula
k = 1..6 y escribe resultados/rendimiento_kmers.csv con la estimación para las 239.946.
"""

import csv, os, sys, time
from itertools import islice
from multiprocessing import Pool
from Bio import SeqIO
sys.path.insert(0, os.getcwd())
from src.kmers import all_kmer_counts

N, TOTAL = 2000, 239946

if __name__ == "__main__":
    seqs = [str(r.seq) for r in islice(SeqIO.parse("data/PanTEon_Database_v1.6.1.fasta", "fasta"), N)]
    nt = sum(map(len, seqs))
    filas = []
    def medir(nombre, procesos, f):
        t = time.perf_counter(); f(); dt = time.perf_counter() - t
        sps = N / dt
        filas.append({"modo": nombre, "procesos": procesos, "secuencias": N, "nucleotidos": nt,
                      "segundos": round(dt, 3), "secuencias_por_segundo": round(sps, 1),
                      "estimado_total_min": round(TOTAL / sps / 60, 2)})
        print(filas[-1])
    medir("1 proceso", 1, lambda: [all_kmer_counts(s) for s in seqs])
    p = os.cpu_count()
    with Pool(p) as pool:
        pool.map(all_kmer_counts, seqs[:50])  # calentar los procesos
        medir("multiprocessing", p, lambda: pool.map(all_kmer_counts, seqs, chunksize=50))
    with open("resultados/rendimiento_kmers.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=filas[0]); w.writeheader(); w.writerows(filas)
