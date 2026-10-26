# Modelo de datos

Este archivo es el contrato del equipo: todos los notebooks usan los nombres de colecciones y
campos definidos aquí. Cualquier cambio se discute antes y se registra en el historial al final.

**Estado:** estructura congelada (2026-10-26). Las colecciones, campos, índices y validadores descritos
aquí son los implementados en `notebooks/01`–`03` y ya no cambian; cualquier cambio posterior se discute con
el equipo y se registra en el historial. La conclusión de la decisión 4 queda pendiente del benchmark de
consultas.

Bases de datos: `panteon` (modelo principal) y `panteon_bench` (solo `tes_embebidos`, para el benchmark).

## Relaciones

```
especies ──1:N──► tes ──1:1──► secuencias
                   │
                   └──1:6──► kmers (un documento por k)

panteon_bench.tes_embebidos (1:1 con tes, mismo _id; solo benchmark)
```

## Decisiones de diseño

| # | Decisión | Elección | Alternativas descartadas |
| --- | --- | --- | --- |
| 1 | Relación TE–especie | Híbrido: referencia `species_id` + copia de `species_name`, `kingdom`, `phylum`, `source` | Solo referencia; especie embebida completa |
| 2 | Jerarquías | Subdocumentos: `taxonomy` en `especies` y `classification` en `tes` | Campos planos; arreglo de ancestros; colección de clasificaciones |
| 3 | Secuencia de ADN | Colección aparte `secuencias`, con el mismo `_id` que su TE | Dentro del documento de `tes` |
| 4 | Ubicación de los k-mers | Colección `kmers`, un documento por TE y por k, copiando `pdb_id` y `te_order` | Embebidos en `tes` (implementada como `tes_embebidos` para el benchmark); un documento por TE con los 6 k; una colección por k |
| 5 | Formato de los k-mers | Conteos en diccionario disperso + `valid_windows` | Arreglo denso; arreglo de pares; binario; frecuencias |

### Justificación resumida

1. **Híbrido.** Los datos son estáticos, así que la duplicación no genera problemas de actualización.
   Se copian solo los campos por los que agrupan o filtran las consultas (2, 3, 4, 6, 7, 9, 10, 11 y 13).
   La referencia se mantiene para el `$lookup` (consulta 12) y la taxonomía completa (consulta 8).
   Embeber la especie completa repetiría `taxonomy`, `notes` y `source_2` en 239.946 documentos; usar solo
   la referencia obligaría a un `$lookup` en casi todas las agregaciones.
2. **Subdocumentos.** Agrupan cada jerarquía y evitan confundir la clase y el orden taxonómicos de la
   especie con la clase y el orden del TE. Los 239.946 TEs tienen exactamente 3 niveles de clasificación
   (`resultados/inconsistencias_fasta.csv`), así que no hace falta un arreglo de ancestros de largo variable.
3. **Secuencias aparte.** La secuencia es la mayor parte del peso de un TE (longitud media 4.017 nt frente
   a 308 B de un documento de `tes`, `avgObjSize` en `resultados/benchmark_espacio.csv`) y solo la usan el
   cálculo de k-mers y las bibliotecas; separarla deja `tes` liviana para las agregaciones (70,5 MB sin
   comprimir).
4. **Un documento por TE y por k.** La consulta 15 y el heatmap usan un solo k a la vez; así cada consulta
   lee solo el k que necesita. Evidencia actual del benchmark de carga y espacio (n = 3, misma máquina,
   validación `$jsonSchema` en ambas estrategias; `resultados/benchmark_carga.csv`,
   `resultados/benchmark_espacio.csv`, `notebooks/06_benchmark_carga_espacio.ipynb`):

   | Medida | `kmers` (colección) | `tes_embebidos` (embebida) |
   | --- | --- | --- |
   | Documentos | 1.439.676 | 239.946 |
   | Carga total (media ± DE, s) | 197,7 ± 2,0 | 186,8 ± 1,8 |
   | Cálculo / inserción / índices (s) | 125,5 / 50,2 / 22,0 | 125,8 / 47,9 / 13,1 |
   | `storageSize` (MB) | 3.030,6 | 3.037,0 (incluye la copia de `tes`, 12,1 MB) |
   | `totalIndexSize` (MB) | 57,7 | 5,2 |

   La embebida carga un 5,5 % más rápido; la diferencia sale sobre todo de la creación de índices (8,9 s)
   y en menor medida de la inserción (2,3 s). En disco los datos ocupan prácticamente lo mismo y los
   índices de `kmers` ocupan unas 11 veces más. **Con carga y espacio la alternativa no pierde.** La
   conclusión de esta decisión depende del **benchmark de consultas (pendiente, responsable: Thomas)**, que
   compara el acceso a un solo k (consulta 15, heatmap de 2-mers) contra el acceso al perfil completo.
5. **Conteos dispersos.** Los conteos son exactos y las frecuencias se derivan como
   `counts / valid_windows`; guardar frecuencias perdería exactitud. El diccionario es autodescriptivo
   (cada valor dice qué k-mer es) y no guarda ceros. El ahorro frente a un arreglo denso depende de la
   longitud: en las secuencias cortas (el 25 % mide menos de 1.463 nt) faltan muchos 5- y 6-mers, pero en
   una secuencia de longitud mediana (4.259 nt) hay más ventanas que 6-mers posibles y casi todos aparecen.
   Ese ahorro no se midió; el benchmark compara ubicación (colección aparte frente a embebidos), no formato.

## Colecciones

### `especies` (2.790 documentos)

Carga: `notebooks/01_pipeline_csv_especies.ipynb`. Es idempotente: `bulk_write` con
`ReplaceOne({"species": ...}, doc, upsert=True)` conserva los `_id` al re-ejecutar (de ellos dependen
`tes.species_id`), y si la colección existe el validador se aplica con `collMod`.

| Campo | Tipo | Origen | Notas |
| --- | --- | --- | --- |
| `_id` | ObjectId | MongoDB | Se conserva entre re-ejecuciones |
| `species` | string | CSV `Species` (con `strip`) | Nombre original del CSV. Índice único |
| `taxonomy.kingdom` | string | CSV `Kingdom` | `Animalia`, `Plantae` o `Fungi` |
| `taxonomy.phylum` | string / null | CSV `Phylum` | `null` si falta |
| `taxonomy.class` | string / null | CSV `Class` | Clase taxonómica, no la del TE. `null` si falta |
| `taxonomy.order` | string / null | CSV `Order` | Orden taxonómico, no el del TE. Los 26 rellenos `No …`/`Not …` pasan a `null` (55 `null` en total) |
| `taxonomy.family` | string / null | CSV `Family` | `null` si falta |
| `source` | string | CSV `Source` | `RM2+MCH` o `Dfam` |
| `source_2` | string / null | CSV `Source 2` | Solo fuentes (`Repbase`, `Dfam`, `RM2+MCH`); los 4 comentarios pasan a `null` |
| `notes` | string / null | CSV `Notes` | |
| `is_species` | bool | Calculado | `false` en 45 entradas que son grupos taxonómicos (44 marcadas con "no especie" en `Notes` + `Muroidea`), como `Homininae`; tienen TEs, por eso se cargan marcadas y no se excluyen |

**Llave de cruce con el FASTA:** `src/normalizacion.py::normalize_species` (quita puntos, espacios al
inicio y al final, reduce espacios repetidos y pasa a minúsculas). Solo se usa para comparar; no se guarda.

Ejemplo real (salida de la sección 1 del notebook 01):

```json
{
  "_id": ObjectId("..."),
  "species": "Abortiporus biennis",
  "taxonomy": {
    "kingdom": "Fungi",
    "phylum": "Basidiomycota",
    "class": "Agaricomycetes",
    "order": "Polyporales",
    "family": "Podoscyphaceae"
  },
  "source": "RM2+MCH",
  "source_2": null,
  "notes": "B-GUT",
  "is_species": true
}
```

### `tes` (239.946 documentos)

Carga: `notebooks/02_pipeline_fasta_tes.ipynb`, por lotes de 2.000 con `insert_many(ordered=False)`.

| Campo | Tipo | Origen | Notas |
| --- | --- | --- | --- |
| `_id` | ObjectId | Generado en Python | Compartido con `secuencias` y `tes_embebidos` |
| `pdb_id` | string | Encabezado, antes de `#` | Identificador original, con dos formatos (ver abajo). Índice único |
| `species_id` | ObjectId | Cruce con `normalize_species` | Referencia a `especies._id` |
| `species_name` | string | Encabezado, después de `@` | Nombre tal como viene en el FASTA (ver abajo) |
| `kingdom` | string | `especies.taxonomy.kingdom` | Copia |
| `phylum` | string / null | `especies.taxonomy.phylum` | Copia; `null` si falta en el CSV |
| `source` | string | `especies.source` | Copia |
| `classification.te_class` | string | Encabezado | |
| `classification.te_order` | string | Encabezado | |
| `classification.te_superfamily` | string | Encabezado | Puede repetir el orden (ver Calidad de datos) |
| `length` | int | Calculado | Longitud total, mínimo 81 y máximo 19.926 nt |
| `gc_content` | double | Calculado | `(G + C) / (A + C + G + T)` sobre la secuencia en mayúsculas; N fuera del denominador |
| `n_percent` | double | Calculado | `N / length` sobre la secuencia en mayúsculas |

**`pdb_id`:** `PDB` + 8 dígitos en las bibliotecas generadas con RM2+MCH (207.813); nombre original de la
biblioteca en 31.600 TEs: 31.592 de especies con `Source = Dfam` y 8 de *Chlamydomonas reinhardtii*
(`Source 2 = Repbase`). Se toma todo lo anterior a `#` sin exigir patrón; no hay duplicados.

**`species_name`:** guarda el nombre tal como viene en el FASTA, para que las bibliotecas `.fasta`
reproduzcan el encabezado original. Difiere de `especies.species` en 4 especies (533 TEs) por la puntuación
de `subsp.`/`sp.` (`resultados/reporte_cruce.md`). Para filtrar por especie se usa `species_id` o el nombre
normalizado con `normalize_species`.

**Campos copiados y su uso:** `kingdom` (consultas por reino y biblioteca por reino), `species_name`
(consulta 9 y biblioteca por especie), `phylum` y `source` (agrupaciones; consulta 13 por Source).

`gc_content` y `n_percent` se guardan sin redondear. Ninguna secuencia carece de A, C, G y T, así que
`gc_content` está definido en todos los TEs.

Ejemplo real (primer registro del FASTA; `_id` y `species_id` dependen de la carga):

```json
{
  "_id": ObjectId("..."),
  "pdb_id": "PDB00000001",
  "species_id": ObjectId("..."),
  "species_name": "Halicephalobus mephisto",
  "kingdom": "Animalia",
  "phylum": "Nematoda",
  "source": "RM2+MCH",
  "classification": {
    "te_class": "CLASSII",
    "te_order": "HELITRON",
    "te_superfamily": "HELITRON"
  },
  "length": 1991,
  "gc_content": 0.3154,
  "n_percent": 0.0
}
```

(`gc_content` redondeado aquí a 4 decimales; en la base va completo.)

### `secuencias` (239.946 documentos)

| Campo | Tipo | Notas |
| --- | --- | --- |
| `_id` | ObjectId | El mismo `_id` de su TE |
| `sequence` | string | Tal como viene en el FASTA, sin modificar: conserva las minúsculas (208.354 secuencias; convención de formato de las bibliotecas de origen) y las N |

Ejemplo real (secuencia truncada):

```json
{ "_id": ObjectId("..."), "sequence": "aaaaaacaaaagaacttaaattttttaaaatttcaatataaaaaaaattttaaatttttt..." }
```

### `kmers` (1.439.676 documentos)

Carga: `notebooks/03_pipeline_kmers.ipynb` con `src/kmers.py::all_kmer_counts`. Exactamente 6 documentos
por TE (verificado en la sección 6 del notebook 03).

| Campo | Tipo | Notas |
| --- | --- | --- |
| `_id` | ObjectId | |
| `te_id` | ObjectId | Referencia a `tes._id` |
| `pdb_id` | string | Copia, para la consulta 15 (perfil por identificador) |
| `te_order` | string | Copia de `classification.te_order`, para el heatmap de 2-mers por orden |
| `k` | int | De 1 a 6 |
| `valid_windows` | int | Ventanas (deslizamiento de 1) sin caracteres distintos de A, C, G, T. 0 si el TE es más corto que k |
| `counts` | object | Solo los k-mers presentes. `{}` si el TE es más corto que k |

Los conteos se calculan sobre la secuencia en mayúsculas; se descarta toda ventana que contenga N (u otro
carácter distinto de A, C, G, T). Los TEs más cortos que k se guardarían igual, con `valid_windows = 0` y
`counts = {}`; en los datos reales no ocurre (longitud mínima 81).

Ejemplo real (k = 2 del primer registro del FASTA):

```json
{
  "_id": ObjectId("..."),
  "te_id": ObjectId("..."),
  "pdb_id": "PDB00000001",
  "te_order": "HELITRON",
  "k": 2,
  "valid_windows": 1990,
  "counts": {
    "AA": 306, "AC": 74, "AG": 110, "AT": 229, "CA": 97, "CC": 45, "CG": 53, "CT": 102,
    "GA": 123, "GC": 75, "GG": 55, "GT": 78, "TA": 193, "TC": 103, "TG": 113, "TT": 234
  }
}
```

**Ojo al promediar:** los k-mers ausentes no aparecen en `counts`. Para promedios (heatmap), sumar las
frecuencias y dividir por el número total de secuencias del grupo, no usar `$avg` después de `$unwind`.

### `tes_embebidos` (base `panteon_bench`, 239.946 documentos)

Estrategia alternativa de k-mers, cargada por `notebooks/03_pipeline_kmers.ipynb`. Existe **solo para el
benchmark**: no forma parte del modelo principal y no la usan las consultas, las figuras ni las bibliotecas.

Cada documento tiene todos los campos de `tes`, el **mismo `_id`** que su TE y un subdocumento `kmers`
con el mismo formato disperso.

Ejemplo esquemático (los `"..."` reemplazan valores reales):

```json
{
  "_id": ObjectId("..."),
  "pdb_id": "PDB00000001",
  "...": "resto de campos de tes",
  "kmers": {
    "k1": { "valid_windows": 1991, "counts": { "A": "..." } },
    "k2": { "valid_windows": 1990, "counts": { "AA": 306, "...": "..." } },
    "k6": { "valid_windows": "...", "counts": { "...": "..." } }
  }
}
```

## Índices

Todos se crean **después** de la carga. Tamaños en MB (1024² bytes) de `resultados/benchmark_espacio.csv`
(colecciones de la repetición 3).

| Colección | Índice | Uso | Tamaño |
| --- | --- | --- | --- |
| `especies` | `{species: 1}` único | Búsqueda por nombre; impide especies duplicadas | no medido |
| `tes` | `{pdb_id: 1}` único | Consulta 8; garantiza identificadores sin duplicados | 2,8 |
| `tes` | `{species_id: 1}` | `$lookup` (consulta 12) y TEs de una especie | 1,7 |
| `tes` | `{species_name: 1, "classification.te_superfamily": 1}` | Consulta 9 y biblioteca por especie | 2,5 |
| `tes` | `{kingdom: 1}` | Consultas por reino y biblioteca por reino | 1,1 |
| `kmers` | `{te_id: 1, k: 1}` único | Perfil de un TE para un k; impide duplicados | 15,7 |
| `kmers` | `{pdb_id: 1, k: 1}` | Consulta 15 por identificador | 19,4 |
| `kmers` | `{k: 1, te_order: 1}` | Heatmap de 2-mers por orden | 7,5 |
| `tes_embebidos` | `{pdb_id: 1}` único | Réplica del índice único de `tes` | 2,8 |

Índices `_id`: `tes` 2,3 MB; `kmers` 15,1 MB; `tes_embebidos` 2,4 MB. Totales: `tes` 10,4 MB; `kmers`
57,7 MB; `tes_embebidos` 5,2 MB.

Su utilidad en consultas se evalúa con `explain("executionStats")` en el benchmark de consultas.

## Validación de esquema (`$jsonSchema`)

Todos los validadores usan `validationLevel: "strict"` y `validationAction: "error"`.

| Colección | Obligatorios | Reglas de tipo y rango |
| --- | --- | --- |
| `especies` | `species`, `taxonomy`, `taxonomy.kingdom`, `is_species` | `kingdom` en {`Animalia`, `Fungi`, `Plantae`}; `phylum`, `class`, `order`, `family`, `source_2` y `notes` string o null; `source` string; `is_species` bool |
| `tes` | `pdb_id`, `species_id`, `species_name`, `kingdom`, `phylum`, `source`, `classification` (con `te_class`, `te_order`, `te_superfamily`), `length`, `gc_content`, `n_percent` | `pdb_id` string sin patrón; `species_id` objectId; `kingdom` enum de 3 reinos; `phylum` string o null; niveles de `classification` string; `length` int/long ≥ 1; `gc_content` y `n_percent` double en [0, 1] |
| `kmers` | `te_id`, `pdb_id`, `te_order`, `k`, `valid_windows`, `counts` | `te_id` objectId; `k` int en [1, 6]; `valid_windows` int/long ≥ 0; `counts` object |
| `tes_embebidos` | Los de `tes` + `kmers` (con `k1`–`k6`, cada uno con `valid_windows` y `counts`) | Reutiliza el validador de `tes` leído de la base (`listCollections`), más `valid_windows` int/long ≥ 0 y `counts` object por cada k |
| `secuencias` | — | Sin validador: se guarda tal como viene del FASTA |

## Calidad de datos y decisiones de limpieza

Detalle: tabla de decisiones de `notebooks/00_exploracion.ipynb` (FASTA), `resultados/reporte_calidad_csv.md`
(CSV) y `resultados/reporte_cruce.md` (cruce).

| Hallazgo | Casos | Decisión en el modelo |
| --- | --- | --- |
| Identificadores sin formato `PDB` + 8 dígitos | 31.600 (31.592 Dfam, 8 de *C. reinhardtii*) | `pdb_id` guarda el original; validador sin patrón; índice único |
| Superfamilia igual al orden | 21.544 en tres grupos: 5.589 correctos (HELITRON, CRYPTON, MAVERICK, PLE); 10.319 clasificados solo hasta orden (TIR, LINE, LTR, SINE); 5.636 ambiguos (MITE 3.456, DIRS 2.067, RETROPOSON 113) | Se cargan tal cual. En los correctos el orden tiene una única superfamilia homónima (Wicker et al., 2007); los clasificados solo hasta orden se reportan como tales en el control de calidad; los ambiguos se reportan aparte, sin reinterpretarlos |
| Secuencias con minúsculas | 208.354 (87 %) | `sequence` sin modificar; GC y k-mers sobre mayúsculas |
| Secuencias con N | 54.837 (23 %; mediana 0,9 % de N) | Se conservan; N fuera del denominador del GC; ventanas con N descartadas (`valid_windows`) |
| Especies que no cruzaban por puntuación | 4 especies, 533 TEs | `normalize_species` quita los puntos: 0 TEs sin especie; `TE_count` del CSV coincide en 2.790 de 2.790 |
| Entradas que no son especies | 45 (p. ej. *Homininae*, 1.173 TEs) | `is_species: false`; sus TEs se conservan |
| Rellenos y espacios en la taxonomía | 26 rellenos de `Order`; 13 con espacios | `strip`; rellenos y vacíos → `null` |
| Inconsistencias taxonómicas por género | 10 géneros, 18 filas | Se cargan tal cual y se documentan. Ej.: *Beta vulgaris* en Amaranthaceae y la subsp. *vulgaris* en Chenopodiaceae, nombre antiguo incluido hoy en Amaranthaceae según APG |

## Integridad referencial y reproducibilidad

MongoDB no garantiza que `tes.species_id` y `kmers.te_id` apunten a documentos existentes. El pipeline lo
protege así:

- **Orden de carga:** 01 (`especies`) → 02 (`tes`, `secuencias`) → 03 (`kmers`, `tes_embebidos`). El 02
  verifica que todo `species_id` existe en `especies` y que `tes` y `secuencias` tienen los mismos `_id`;
  el 03 verifica 6 documentos por TE.
- **`especies` idempotente:** el 01 se puede re-ejecutar sin cambiar los `_id` (`ReplaceOne` con `upsert`).
- **Guarda `RECONSTRUIR_TODO` en el 02:** recargar `tes` genera `_id` nuevos y dejaría huérfanos a `kmers` y
  `tes_embebidos`. Si alguna de las dos tiene datos, el 02 se detiene salvo que `RECONSTRUIR_TODO = True`, y
  en ese caso hay que ejecutar después el 03.
- La alternativa a reconstruir es restaurar el dump (`resultados/dump_info.md`).

## Pendientes

| Pendiente | Responsable | Estado |
| --- | --- | --- |
| Qué hacer con los TEs cuya especie no está en el CSV | Juan Arias propone, Thomas aplica | Cerrado: 0 TEs sin especie tras `normalize_species` (`src/normalizacion.py`); antes de quitar los puntos eran 533 (`resultados/reporte_cruce.md`) |
| Tratamiento de ventanas con N u otros caracteres | Juan Arias | Cerrado: se descarta toda ventana con un carácter distinto de A, C, G, T; `valid_windows` cuenta solo las válidas (`src/kmers.py`) |
| Reglas de `$jsonSchema` para `tes` y `kmers` | Thomas | Cerrado: implementadas en los notebooks 02 y 03 (sección Validación de esquema) |
| Estrategia alternativa de k-mers para el benchmark | Thomas y Juan Arias | Cerrado: `panteon_bench.tes_embebidos`, medida en carga y espacio con n = 3 (`notebooks/06_benchmark_carga_espacio.ipynb`) |
| Normalización de valores "No order…" y espacios en la taxonomía | Juan Arias | Cerrado: 26 rellenos de `Order` → `null`; `strip` en todas las columnas; vacíos → `null` (notebook 01) |
| Benchmark de consultas (acceso a un k frente al perfil completo; con y sin índices) | Thomas | Abierto: define la conclusión de la decisión 4 (`notebooks/06_benchmark_consultas.ipynb`) |

## Historial de cambios

| Fecha | Cambio | Quién |
| --- | --- | --- |
| 2026-10-24 | Primer borrador del modelo | Thomas |
| 2026-10-25 | `is_species` y validación en `especies`; TEs más cortos que k en `kmers`; cierre de pendientes de cruce, ventanas con N y normalización | Juan Arias |
| 2026-10-26 | Estructura congelada: modelo alineado con lo implementado (notebooks 01–03); `tes_embebidos`, validadores reales, tamaños de índices, calidad de datos, integridad referencial y evidencia del benchmark de carga y espacio en la decisión 4 | Thomas |
