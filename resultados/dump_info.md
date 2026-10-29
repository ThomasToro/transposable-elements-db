# Dumps de la base real

Generados el 2026-10-26 con `mongodump` 100.16.1 sobre MongoDB 7.0 local. Los dumps no se suben al
repositorio (`dump/` está en `.gitignore`); se comparten por Google Drive como `.tar` (sin comprimir de nuevo: los `.bson.gz` de adentro ya van comprimidos).
Tamaños en MB de 1024² bytes.

## Archivos para Google Drive

Carpeta: https://drive.google.com/drive/folders/1dralHzwDjck0lAboxCMs4UODyhWXVpbY

| Archivo | Tamaño | Contenido |
| --- | --- | --- |
| `dump/panteon_kmers.tar` | 2.111,7 MB (2.214.315.008 bytes) | Base `panteon`: `especies`, `tes`, `secuencias`, `kmers` |
| `dump/panteon_bench.tar` | 1.941,6 MB (2.035.924.992 bytes) | Base `panteon_bench`: `tes_embebidos` (benchmark de consultas) |

## Tamaño por colección (`.bson.gz`)

| Dump | Colección | Documentos | Tamaño |
| --- | --- | --- | --- |
| `panteon_kmers` | `especies` | 2.790 | 0,07 MB (73.918 bytes) |
| `panteon_kmers` | `tes` | 239.946 | 5,9 MB (6.217.292 bytes) |
| `panteon_kmers` | `secuencias` | 239.946 | 204,0 MB (213.932.194 bytes) |
| `panteon_kmers` | `kmers` | 1.439.676 | 1.901,7 MB (1.994.058.528 bytes) |
| `panteon_kmers` | **Total carpeta** | | 2,1 GB (`du -sh`) |
| `panteon_bench` | `tes_embebidos` | 239.946 | 1.941,6 MB (2.035.909.451 bytes) |
| `panteon_bench` | **Total carpeta** | | 1,9 GB (`du -sh`) |

## Verificación de la restauración

`dump/panteon_kmers` se restauró en una base temporal `panteon_verif` y se comparó con `panteon`;
luego `panteon_verif` se borró.

| Colección | Documentos en `panteon` | Documentos restaurados | Índices | Validador `$jsonSchema` |
| --- | --- | --- | --- | --- |
| `especies` | 2.790 | 2.790 | 2, iguales | igual |
| `tes` | 239.946 | 239.946 | 5, iguales | igual |
| `secuencias` | 239.946 | 239.946 | 1, igual | igual (sin validador) |
| `kmers` | 1.439.676 | 1.439.676 | 4, iguales | igual |

La restauración tardó 1 min 11 s (incluye la reconstrucción de índices). `panteon_bench` no se
restauró para verificar.

Los dumps se regeneraron el 2026-10-26 después de las 3 repeticiones definitivas del benchmark de carga
(las colecciones `kmers` y `tes_embebidos` son las de la repetición 3). Ambas estrategias se cargaron con
validación de esquema (`$jsonSchema`, `strict`, `error`): `kmers` con `ESQUEMA_KMERS` y `tes_embebidos` con el
validador de `tes` más el perfil `kmers.k1`–`k6`. Los validadores van en los `*.metadata.json.gz` del dump y
`mongorestore` los vuelve a crear. La verificación de arriba se hizo con un dump anterior; los conteos de
documentos no cambiaron y `especies`, `tes` y `secuencias` no se recargaron, así que no se repitió la restauración.

## Cómo restaurar (para el README)

Requiere MongoDB 7.0 y MongoDB Database Tools. Descargar los `.tar` de la
[carpeta de Google Drive](https://drive.google.com/drive/folders/1dralHzwDjck0lAboxCMs4UODyhWXVpbY) en la
raíz del repositorio y ejecutar:

```bash
mkdir -p dump

# Base principal: especies, tes, secuencias y kmers
tar -xf panteon_kmers.tar -C dump/
mongorestore --gzip --drop dump/panteon_kmers

# Base del benchmark: tes_embebidos
tar -xf panteon_bench.tar -C dump/
mongorestore --gzip --drop dump/panteon_bench
```

`--drop` borra antes cada colección que ya exista con el mismo nombre. Para restaurar con otro nombre de
base (por ejemplo, para no tocar una `panteon` existente):

```bash
mongorestore --gzip --nsFrom "panteon.*" --nsTo "otra_base.*" dump/panteon_kmers
```

**Reconstruir desde cero (sin dump):** ejecutar en orden `01_pipeline_csv_especies.ipynb` →
`02_pipeline_fasta_tes.ipynb` (con `RECONSTRUIR_TODO = True`) → `03_pipeline_kmers.ipynb`. El 01 se puede
re-ejecutar solo: actualiza `especies` por la llave `species` sin cambiar los `_id`. El 02 se detiene si
`kmers` o `panteon_bench.tes_embebidos` tienen datos, porque al recargar `tes` cambian sus `_id`; con
`RECONSTRUIR_TODO = True` continúa y luego hay que ejecutar el 03. La alternativa es restaurar el dump.

Comandos con los que se generaron:

```bash
# Los dos dumps se pueden ejecutar en paralelo (unos 7,5 min en total)
mongodump --gzip --db panteon --out dump/panteon_kmers &
mongodump --gzip --db panteon_bench --out dump/panteon_bench &
wait
cd dump && tar -cf panteon_kmers.tar panteon_kmers && tar -cf panteon_bench.tar panteon_bench
```
