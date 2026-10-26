from src.normalizacion import normalize_species


def test_normalize_species():
    assert normalize_species("  Puma   concolor ") == "puma concolor"
    assert normalize_species("Puma\tConcolor") == "puma concolor"


def test_puntos_subsp_sp():
    assert normalize_species("Beta vulgaris subsp. vulgaris") == normalize_species("Beta vulgaris subsp vulgaris")
    assert normalize_species("Coccomyxa sp. obi") == normalize_species("Coccomyxa sp obi")


def test_forma_especial():
    assert (normalize_species("Blumeria graminis f. sp. tritici")
            == normalize_species("Blumeria graminis f sp tritici")
            == "blumeria graminis f sp tritici")
