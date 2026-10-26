# Reporte de calidad del FASTA

Generado por `notebooks/02_pipeline_fasta_tes.ipynb` al cargar `tes` y `secuencias` en `panteon`. Exploración previa: `notebooks/00_exploracion.ipynb` y `resultados/inconsistencias_fasta.csv`.

| Hallazgo | Valor |
| --- | --- |
| Registros en el FASTA | 239946 |
| Encabezados mal formados (sin un único `#` y un único `@`) | 0 |
| Clasificaciones con menos de 3 niveles | 0 |
| `pdb_id` duplicados | 0 |
| `pdb_id` con prefijo distinto de `PDB` + 8 dígitos (se aceptan) | 31600 |
| Caracteres fuera de A, C, G, T, N (en mayúsculas) | ninguno |
| Secuencias con minúsculas (se guardan sin modificar) | ver `resultados/inconsistencias_fasta.csv` |
| Secuencias con N | 54837 |
| Longitud mínima / máxima (nt) | 81 / 19926 |
| Secuencias de longitud cero | 0 |
| TEs sin especie tras `normalize_species` | 0 |
| Documentos en `tes` / `secuencias` | 239946 / 239946 |

## Decisiones

- `pdb_id`: se toma todo lo anterior a `#`, sin asumir el prefijo `PDB`.
- `gc_content = (G + C) / (A + C + G + T)`: excluye N e IUPAC del denominador; `n_percent = N / length`. Ambos sobre la secuencia en mayúsculas.
- `secuencias.sequence` guarda la secuencia original sin modificar (minúsculas incluidas).
- `species_id` se obtiene con `src.normalizacion.normalize_species` (ver `resultados/reporte_cruce.md`); `species_name` guarda el nombre tal como viene en el FASTA.
- `phylum` se copia de `especies` y puede ser `null` cuando falta en el CSV.
