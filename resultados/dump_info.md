# Dumps de la base real

Generados el 2026-10-25 con `mongodump` 100.16.1 sobre MongoDB 7.0 local. Los dumps no se suben al
repositorio (`dump/` está en `.gitignore`); se comparten por Google Drive como `.tar.gz`.
Tamaños en MB de 1024² bytes.

## Archivos para Google Drive

| Archivo | Tamaño | Contenido |
| --- | --- | --- |
| `dump/panteon_kmers.tar.gz` | 2.097,4 MB (2.199.303.316 bytes) | Base `panteon`: `especies`, `tes`, `secuencias`, `kmers` |
| `dump/panteon_bench.tar.gz` | 1.925,9 MB (2.019.499.905 bytes) | Base `panteon_bench`: `tes_embebidos` (benchmark de consultas) |

## Tamaño por colección (`.bson.gz`)

| Dump | Colección | Documentos | Tamaño |
| --- | --- | --- | --- |
| `panteon_kmers` | `especies` | 2.790 | 0,07 MB (73.918 bytes) |
| `panteon_kmers` | `tes` | 239.946 | 5,9 MB (6.217.292 bytes) |
| `panteon_kmers` | `secuencias` | 239.946 | 204,0 MB (213.932.194 bytes) |
| `panteon_kmers` | `kmers` | 1.439.676 | 1.901,6 MB (1.994.016.082 bytes) |
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

## Cómo restaurar (para el README)

Requiere MongoDB 7.0 y MongoDB Database Tools. Descargar los `.tar.gz` de Google Drive en la raíz del
repositorio y ejecutar:

```bash
mkdir -p dump

# Base principal: especies, tes, secuencias y kmers
tar -xzf panteon_kmers.tar.gz -C dump/
mongorestore --gzip --drop dump/panteon_kmers

# Base del benchmark: tes_embebidos
tar -xzf panteon_bench.tar.gz -C dump/
mongorestore --gzip --drop dump/panteon_bench
```

`--drop` borra antes cada colección que ya exista con el mismo nombre. Para restaurar con otro nombre de
base (por ejemplo, para no tocar una `panteon` existente):

```bash
mongorestore --gzip --nsFrom "panteon.*" --nsTo "otra_base.*" dump/panteon_kmers
```

Comandos con los que se generaron:

```bash
mongodump --gzip --db panteon --out dump/panteon_kmers
mongodump --gzip --db panteon_bench --out dump/panteon_bench
cd dump && tar -czf panteon_kmers.tar.gz panteon_kmers && tar -czf panteon_bench.tar.gz panteon_bench
```
