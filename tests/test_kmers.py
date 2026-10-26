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
