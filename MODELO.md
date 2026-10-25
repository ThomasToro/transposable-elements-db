# Modelo de datos

Este archivo es el contrato del equipo: todos los notebooks usan los nombres de colecciones y
campos definidos aquí. Cualquier cambio se discute antes y se registra en el historial al final.

**Estado:** borrador. Se congela después de la exploración, antes del primer dump.

Base de datos: `panteon`

## Relaciones

```
especies ──1:N──► tes ──1:1──► secuencias
                   │
                   └──1:6──► kmers (un documento por k)
```

## Decisiones de diseño

| # | Decisión | Elección | Alternativas descartadas |
| --- | --- | --- | --- |
| 1 | Relación TE–especie | Híbrido: referencia `species_id` + copia de `species_name`, `kingdom`, `phylum`, `source` | Solo referencia; especie embebida completa |
| 2 | Jerarquías | Subdocumentos: `taxonomy` en `especies` y `classification` en `tes` | Campos planos; arreglo de ancestros; colección de clasificaciones |
| 3 | Secuencia de ADN | Colección aparte `secuencias`, con el mismo `_id` que su TE | Dentro del documento de `tes` |
| 4 | Ubicación de los k-mers | Colección `kmers`, un documento por secuencia y por k, copiando `te_order` | Embebidos en `tes`; un documento por secuencia; una colección por k |
| 5 | Formato de los k-mers | Conteos en diccionario disperso + `valid_windows` | Arreglo denso; arreglo de pares; binario; frecuencias |

### Justificación resumida

1. **Híbrido.** Los datos son estáticos, así que la duplicación no genera problemas de actualización.
   Se copian solo los campos por los que agrupan o filtran las consultas (2, 3, 4, 6, 7, 9, 10, 11 y 13).
   La referencia se mantiene para el `$lookup` (consulta 12) y la taxonomía completa (consulta 8).
2. **Subdocumentos.** Agrupan cada jerarquía y evitan confundir la clase y el orden taxonómicos de la
   especie con la clase y el orden del TE.
3. **Secuencias aparte.** La secuencia es más del 90 % del peso de un TE y solo la usan el cálculo de
   k-mers y las bibliotecas; separarla deja `tes` liviana para las agregaciones.
4. **Un documento por secuencia y por k.** La consulta 15 y el heatmap usan un solo k a la vez; así cada
   consulta lee solo el k que necesita.
5. **Conteos dispersos.** Los conteos son exactos y las frecuencias se derivan con `valid_windows`;
   el diccionario no guarda ceros, que abundan en k = 5 y 6.

## Colecciones

### `especies` (~2.790 documentos)

| Campo | Tipo | Origen | Notas |
| --- | --- | --- | --- |
| `_id` | ObjectId | MongoDB | |
| `species` | string | CSV `Species` | Llave del cruce con el FASTA. Índice único |
| `taxonomy.kingdom` | string | CSV `Kingdom` | |
| `taxonomy.phylum` | string | CSV `Phylum` | Puede faltar |
| `taxonomy.class` | string | CSV `Class` | Clase taxonómica, no la del TE. Puede faltar |
| `taxonomy.order` | string | CSV `Order` | Orden taxonómico, no el del TE. Puede faltar |
| `taxonomy.family` | string | CSV `Family` | Puede faltar |
| `source` | string | CSV `Source` | `RM2+MCH` o `Dfam` |
| `source_2` | string / null | CSV `Source 2` | Casi siempre vacío |
| `notes` | string / null | CSV `Notes` | |

```json
{
  "_id": ObjectId("..."),
  "species": "Halicephalobus mephisto",
  "taxonomy": {
    "kingdom": "Animalia",
    "phylum": "Nematoda",
    "class": "Chromadorea",
    "order": "Rhabditida",
    "family": "Panagrolaimidae"
  },
  "source": "RM2+MCH",
  "source_2": null,
  "notes": "B-GUT"
}
```

### `tes` (~240.000 documentos)

| Campo | Tipo | Origen | Notas |
| --- | --- | --- | --- |
| `_id` | ObjectId | MongoDB | Compartido con `secuencias` |
| `pdb_id` | string | Encabezado, antes de `#` | Índice único |
| `species_id` | ObjectId | Cruce | Referencia a `especies._id` |
| `species_name` | string | Encabezado, después de `@` | Copia |
| `kingdom` | string | `especies` | Copia |
| `phylum` | string | `especies` | Copia |
| `source` | string | `especies` | Copia |
| `classification.te_class` | string | Encabezado | |
| `classification.te_order` | string | Encabezado | |
| `classification.te_superfamily` | string | Encabezado | |
| `length` | int | Calculado | |
| `gc_content` | double | Calculado | Entre 0 y 1 |
| `n_percent` | double | Calculado | Entre 0 y 1 |

```json
{
  "_id": ObjectId("6719a2a8..."),
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
  "length": 2345,
  "gc_content": 0.37,
  "n_percent": 0.0
}
```

### `secuencias` (~240.000 documentos)

| Campo | Tipo | Notas |
| --- | --- | --- |
| `_id` | ObjectId | El mismo `_id` de su TE |
| `sequence` | string | Tal como viene en el FASTA, sin modificar |

### `kmers` (~1,44 millones de documentos)

| Campo | Tipo | Notas |
| --- | --- | --- |
| `_id` | ObjectId | |
| `te_id` | ObjectId | Referencia a `tes._id` |
| `pdb_id` | string | Copia, para la consulta 15 |
| `te_order` | string | Copia, para el heatmap |
| `k` | int | De 1 a 6 |
| `valid_windows` | int | Ventanas contadas (sin caracteres distintos de A, C, G, T) |
| `counts` | object | Solo los k-mers presentes: `{"AA": 221, "AC": 98, ...}` |

```json
{
  "_id": ObjectId("..."),
  "te_id": ObjectId("6719a2a8..."),
  "pdb_id": "PDB00000001",
  "te_order": "HELITRON",
  "k": 2,
  "valid_windows": 2344,
  "counts": { "AA": 221, "AC": 98, "AG": 112 }
}
```

**Ojo al promediar:** los k-mers ausentes no aparecen en `counts`. Para promedios (heatmap), sumar las
frecuencias y dividir por el número total de secuencias del grupo, no usar `$avg` después de `$unwind`.

## Índices

| Colección | Índice | Justificación |
| --- | --- | --- |
| `especies` | `{species: 1}` único | Cruce con el FASTA, búsqueda por nombre |
| `tes` | `{pdb_id: 1}` único | Consulta 8; garantiza PDB sin duplicados |
| `tes` | `{species_id: 1}` | `$lookup` y TEs de una especie |
| `tes` | `{species_name: 1, "classification.te_superfamily": 1}` | Consulta 9 y biblioteca por especie |
| `tes` | `{kingdom: 1}` | Consultas por reino y biblioteca por reino |
| `kmers` | `{te_id: 1, k: 1}` único | Perfil de un TE para un k; impide duplicados |
| `kmers` | `{pdb_id: 1, k: 1}` | Consulta 15 por nombre |
| `kmers` | `{k: 1, te_order: 1}` | Heatmap de 2-mers por orden |

Punto de partida: se confirman o descartan con `explain("executionStats")` en el benchmark.

## Validación de esquema (`$jsonSchema`)

| Colección | ¿Validación? | Motivo |
| --- | --- | --- |
| `tes` | Sí | Colección generada por el pipeline; detecta errores de parseo |
| `kmers` | Sí | Colección generada por el pipeline; garantiza `k` entre 1 y 6 |
| `especies` | No | _(por confirmar)_ |
| `secuencias` | No | Se guardan tal como vienen del FASTA |

Las reglas se escriben después de la exploración, cuando se conozcan los casos raros
(clasificaciones incompletas, campos faltantes).

## Pendientes

| Pendiente | Responsable | Estado |
| --- | --- | --- |
| Qué hacer con los TEs cuya especie no está en el CSV | Juan Arias propone, Thomas aplica | Abierto |
| Tratamiento de ventanas con N u otros caracteres | Juan Arias | Abierto |
| Reglas de `$jsonSchema` para `tes` y `kmers` | Thomas | Después de la exploración |
| Estrategia alternativa de k-mers para el benchmark | Thomas y Juan Arias | Más adelante |
| Normalización de valores "No order…" y espacios en la taxonomía | Juan Arias | Abierto |

## Historial de cambios

| Fecha | Cambio | Quién |
| --- | --- | --- |
| 2026-10-24 | Primer borrador del modelo | Thomas |
