import pytest

from phases.services.finale_seeding import (
    ErreurSeeding,
    generer_paires_premier_tour,
)


def test_seeding_4_equipes_demis():
    equipes = ["E1", "E2", "E3", "E4"]  # déjà triées par seed
    paires = generer_paires_premier_tour(equipes)
    # Demi-finales: 1v4 et 2v3 (standard)
    assert paires == [("E1", "E4"), ("E2", "E3")]


def test_seeding_6_equipes_quarts_avec_bye():
    equipes = ["E1", "E2", "E3", "E4", "E5", "E6"]
    paires = generer_paires_premier_tour(equipes)
    # 8 slots => 4 matchs, 2 BYE
    assert len(paires) == 4
    assert sum(1 for a, b in paires if b is None or a is None) == 2


def test_seeding_8_equipes_quarts_sans_bye():
    equipes = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
    paires = generer_paires_premier_tour(equipes)
    assert len(paires) == 4
    assert all(a is not None and b is not None for a, b in paires)


def test_seeding_12_equipes_huitiemes_avec_bye():
    equipes = [f"E{i}" for i in range(1, 13)]
    paires = generer_paires_premier_tour(equipes)
    # 16 slots => 8 matchs, 4 BYE
    assert len(paires) == 8
    assert sum(1 for a, b in paires if b is None or a is None) == 4


def test_refuse_moins_de_4():
    with pytest.raises(ErreurSeeding):
        generer_paires_premier_tour(["E1", "E2", "E3"])


def test_refuse_plus_de_16():
    with pytest.raises(ErreurSeeding):
        generer_paires_premier_tour([f"E{i}" for i in range(1, 18)])
