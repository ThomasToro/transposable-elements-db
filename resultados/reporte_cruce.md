# Cruce CSV de especies ↔ FASTA

Generado por `notebooks/01_pipeline_csv_especies.ipynb`. Llave de cruce: `src.normalizacion.normalize_species`.

| Medida | Valor |
| --- | --- |
| TEs en el FASTA | 239946 |
| Especies en el FASTA | 2790 |
| Especies en `especies` | 2790 |
| Especies del FASTA que no están en el CSV | 0 |
| Especies del CSV sin TEs en el FASTA | 0 |
| TEs que quedarían sin `species_id` | 0 |

Listas completas: `cruce_fasta_sin_csv.csv` y `cruce_csv_sin_fasta.csv`.

## Causa y solución de los desajustes

Una primera versión de la llave (strip, espacios dobles a uno y minúsculas) dejaba 4 especies sin
pareja y 533 TEs sin `species_id`. Eran los mismos 4 taxones escritos de dos formas: el FASTA abrevia
los rangos infraespecíficos con punto y el CSV sin él.

| FASTA | CSV | TEs |
| --- | --- | --- |
| Beta vulgaris subsp. vulgaris | Beta vulgaris subsp vulgaris | 296 |
| Abrus pulchellus subsp. cantoniensis | Abrus pulchellus subsp cantoniensis | 178 |
| Marchantia polymorpha subsp. montivagans | Marchantia polymorpha subsp montivagans | 48 |
| Coccomyxa sp. obi | Coccomyxa sp obi | 11 |

Solución: `normalize_species` también elimina los puntos antes de comparar. Ningún nombre del CSV
tiene punto y la nueva llave no genera duplicados en el CSV (0 duplicados), así que
el cambio no fusiona especies distintas. En la base se guarda el nombre original del CSV.

## Especies del FASTA que no están en el CSV

Ninguna.

## Especies del CSV sin TEs en el FASTA

Ninguna.

## Comentarios de `Source 2` pasados a null

| Species | Source 2 |
| --- | --- |
| Burhinus oedicnemus | Genero y familia repetido |
| Chironomus riparius | Genero coincidente |
| Chironomus tepperi | Genero coincidente |
| Cucumis sativus | Obtained by Johan P. |
