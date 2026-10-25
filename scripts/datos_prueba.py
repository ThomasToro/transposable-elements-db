"""
Datos de prueba para escribir consultas antes de tener la carga real.

Crea la base `panteon_prueba` con la misma estructura de MODELO.md:
  - especies:   7 especies reales del CSV de PanTEon (taxonomía real)
  - tes:        ~24 TEs INVENTADOS (PDB99xxxxxx), repartidos entre 6 de esas especies
  - secuencias: secuencias INVENTADAS (aleatorias, con semilla fija)
  - kmers:      perfiles k = 1..6 calculados de verdad a partir de esas secuencias

Los TEs, las secuencias y los k-mers NO son datos reales: solo sirven para probar
consultas. Cuando exista la base real (`panteon`), basta con cambiar el nombre de la base.

Casos especiales incluidos a propósito:
  - Una especie sin TEs (Acomys cahirinus), para consultas de calidad y $lookup.
  - Secuencias con N, para probar el manejo de caracteres ambiguos.
  - Una secuencia de 5 nucleótidos, que no tiene 6-mers (valid_windows = 0).

Definiciones provisionales (las define el pipeline real; ver MODELO.md):
  - gc_content = (G + C) / (A + C + G + T)
  - n_percent  = N / longitud
  - Las ventanas de k-mers que contienen un carácter distinto de A, C, G, T se saltan.

Uso, desde la carpeta del proyecto y con el entorno activo:
    python scripts/datos_prueba.py
"""

import random

from pymongo import ASCENDING, MongoClient

URI = "mongodb://localhost:27017"
DB_NAME = "panteon_prueba"
SEED = 42

ESPECIES = [
    {"species": "Halicephalobus mephisto",
     "taxonomy": {"kingdom": "Animalia", "phylum": "Nematoda", "class": "Chromadorea",
                  "order": "Rhabditida", "family": "Panagrolaimidae"},
     "source": "RM2+MCH", "source_2": None, "notes": 'ENSEMBL "2023"'},
    {"species": "Acinonyx jubatus",
     "taxonomy": {"kingdom": "Animalia", "phylum": "Chordata", "class": "Mammalia",
                  "order": "Carnivora", "family": "Felidae"},
     "source": "Dfam", "source_2": None, "notes": "Curated Dfam"},
    {"species": "Acomys cahirinus",  # sin TEs a propósito
     "taxonomy": {"kingdom": "Animalia", "phylum": "Chordata", "class": "Mammalia",
                  "order": "Rodentia", "family": "Muridae"},
     "source": "Dfam", "source_2": None, "notes": "Curated Dfam"},
    {"species": "Acer negundo",
     "taxonomy": {"kingdom": "Plantae", "phylum": "Angiosperma", "class": "Magnoliopsida",
                  "order": "Sapindales", "family": "Sapindaceae"},
     "source": "RM2+MCH", "source_2": None, "notes": 'ENSEMBL "2025"'},
    {"species": "Actinidia chinensis",
     "taxonomy": {"kingdom": "Plantae", "phylum": "Angiosperma", "class": "Magnoliopsida",
                  "order": "Ericales", "family": "Actinidiaceae"},
     "source": "RM2+MCH", "source_2": None, "notes": "Uncurated Dfam"},
    {"species": "Abortiporus biennis",
     "taxonomy": {"kingdom": "Fungi", "phylum": "Basidiomycota", "class": "Agaricomycetes",
                  "order": "Polyporales", "family": "Podoscyphaceae"},
     "source": "RM2+MCH", "source_2": None, "notes": "B-GUT"},
    {"species": "Septoria linicola",
     "taxonomy": {"kingdom": "Fungi", "phylum": "Ascomycota", "class": "Dothideomycetes",
                  "order": "Mycosphaerellales", "family": "Mycosphaerellaceae"},
     "source": "Dfam", "source_2": None, "notes": None},
]

# Clasificaciones de ejemplo (clase, orden, superfamilia). Los nombres reales del FASTA
# pueden ser distintos: se confirman en la exploración.
CLASIFICACIONES = [
    ("CLASSI", "LTR", "GYPSY"),
    ("CLASSI", "LTR", "COPIA"),
    ("CLASSI", "LINE", "L1"),
    ("CLASSII", "TIR", "MARINER"),
    ("CLASSII", "HELITRON", "HELITRON"),
]

# (especie, número de TEs)
TES_POR_ESPECIE = [
    ("Halicephalobus mephisto", 6),
    ("Acinonyx jubatus", 4),
    ("Acer negundo", 5),
    ("Actinidia chinensis", 3),
    ("Abortiporus biennis", 4),
    ("Septoria linicola", 2),
]

ALFABETO = "ACGT"


def secuencia_aleatoria(rng, longitud, gc, con_n=False):
    """Genera una secuencia con un contenido GC aproximado y, opcionalmente, un tramo de N."""
    bases = []
    for _ in range(longitud):
        if rng.random() < gc:
            bases.append(rng.choice("GC"))
        else:
            bases.append(rng.choice("AT"))
    if con_n and longitud > 40:
        inicio = rng.randint(10, longitud - 30)
        tramo = rng.randint(5, 20)
        for i in range(inicio, inicio + tramo):
            bases[i] = "N"
    return "".join(bases)


def atributos(seq):
    a, c, g, t = (seq.count(b) for b in ALFABETO)
    n = seq.count("N")
    validas = a + c + g + t
    return {
        "length": len(seq),
        "gc_content": round((g + c) / validas, 4) if validas else 0.0,
        "n_percent": round(n / len(seq), 4) if seq else 0.0,
    }


def perfil_kmers(seq, k):
    """Cuenta los k-mers presentes, saltando ventanas con caracteres distintos de A, C, G, T."""
    counts = {}
    validas = 0
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i + k]
        if all(b in ALFABETO for b in kmer):
            counts[kmer] = counts.get(kmer, 0) + 1
            validas += 1
    return counts, validas


def main():
    rng = random.Random(SEED)
    client = MongoClient(URI)
    client.drop_database(DB_NAME)  # se puede ejecutar varias veces; siempre parte de cero
    db = client[DB_NAME]

    # especies
    res = db.especies.insert_many(ESPECIES)
    especie_por_nombre = {e["species"]: (oid, e) for oid, e in zip(res.inserted_ids, ESPECIES)}

    # tes, secuencias y kmers
    tes, secuencias, kmers = [], [], []
    numero = 1
    for nombre, cantidad in TES_POR_ESPECIE:
        species_id, esp = especie_por_nombre[nombre]
        for _ in range(cantidad):
            te_class, te_order, te_superfamily = rng.choice(CLASIFICACIONES)
            longitud = rng.choice([80, 250, 600, 1200, 2500, 4000])
            gc = rng.uniform(0.30, 0.60)
            seq = secuencia_aleatoria(rng, longitud, gc, con_n=(numero % 5 == 0))
            tes.append((numero, species_id, esp, (te_class, te_order, te_superfamily), seq))
            numero += 1

    # Una secuencia muy corta (sin 6-mers) para probar casos borde
    species_id, esp = especie_por_nombre["Acer negundo"]
    tes.append((numero, species_id, esp, ("CLASSI", "LTR", "GYPSY"), "ACGTA"))

    docs_tes = []
    for numero, species_id, esp, (te_class, te_order, te_superfamily), seq in tes:
        doc = {
            "pdb_id": f"PDB99{numero:06d}",
            "species_id": species_id,
            "species_name": esp["species"],
            "kingdom": esp["taxonomy"]["kingdom"],
            "phylum": esp["taxonomy"]["phylum"],
            "source": esp["source"],
            "classification": {
                "te_class": te_class,
                "te_order": te_order,
                "te_superfamily": te_superfamily,
            },
            **atributos(seq),
        }
        docs_tes.append((doc, seq))

    res = db.tes.insert_many([d for d, _ in docs_tes])
    for te_id, (doc, seq) in zip(res.inserted_ids, docs_tes):
        secuencias.append({"_id": te_id, "sequence": seq})
        for k in range(1, 7):
            counts, validas = perfil_kmers(seq, k)
            kmers.append({
                "te_id": te_id,
                "pdb_id": doc["pdb_id"],
                "te_order": doc["classification"]["te_order"],
                "k": k,
                "valid_windows": validas,
                "counts": counts,
            })

    db.secuencias.insert_many(secuencias)
    db.kmers.insert_many(kmers)

    # Índices de MODELO.md
    db.especies.create_index([("species", ASCENDING)], unique=True)
    db.tes.create_index([("pdb_id", ASCENDING)], unique=True)
    db.tes.create_index([("species_id", ASCENDING)])
    db.tes.create_index([("species_name", ASCENDING), ("classification.te_superfamily", ASCENDING)])
    db.tes.create_index([("kingdom", ASCENDING)])
    db.kmers.create_index([("te_id", ASCENDING), ("k", ASCENDING)], unique=True)
    db.kmers.create_index([("pdb_id", ASCENDING), ("k", ASCENDING)])
    db.kmers.create_index([("k", ASCENDING), ("te_order", ASCENDING)])

    print(f"Base '{DB_NAME}' creada:")
    for nombre in ["especies", "tes", "secuencias", "kmers"]:
        print(f"  {nombre:<11} {db[nombre].count_documents({}):>4} documentos")
    print("Ejemplo de TE:", db.tes.find_one({}, {"_id": 0, "species_id": 0}))


if __name__ == "__main__":
    main()
