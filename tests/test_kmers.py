from src.kmers import all_kmer_counts, kmer_counts


def test_enunciado_atgca():
    r = all_kmer_counts("ATGCA")
    assert r[1] == {"valid_windows": 5, "counts": {"A": 2, "T": 1, "G": 1, "C": 1}}
    assert r[2] == {"valid_windows": 4, "counts": {"AT": 1, "TG": 1, "GC": 1, "CA": 1}}


def test_n_en_medio():
    # ACGTNACGT: los tramos ACGT y ACGT dan 2 ventanas de k=3 cada uno
    r = kmer_counts("ACGTNACGT", 3)
    assert r["valid_windows"] == 4
    assert r["counts"] == {"ACG": 2, "CGT": 2}
    assert kmer_counts("ACGTNACGT", 1)["valid_windows"] == 8


def test_iupac_descartado():
    assert kmer_counts("ARC", 2) == {"valid_windows": 0, "counts": {}}


def test_secuencia_corta():
    r = all_kmer_counts("ACGTA")
    assert r[6] == {"valid_windows": 0, "counts": {}}
    assert r[5]["valid_windows"] == 1


def test_minusculas():
    assert all_kmer_counts("atgca") == all_kmer_counts("ATGCA")


def _ingenuo(seq, k):
    seq = seq.upper()
    counts = {}
    for i in range(len(seq) - k + 1):
        w = seq[i:i + k]
        if set(w) <= set("ACGT"):
            counts[w] = counts.get(w, 0) + 1
    return {"valid_windows": sum(counts.values()), "counts": counts}


def test_contra_ingenuo():
    import random

    rng = random.Random(0)
    for i in range(50):
        alfabeto = "ACGTacgt" + ("NRY" if i % 3 == 0 else "")
        seq = "".join(rng.choice(alfabeto) for _ in range(rng.randint(0, 300)))
        for k in range(1, 7):
            assert kmer_counts(seq, k) == _ingenuo(seq, k), (seq, k)
