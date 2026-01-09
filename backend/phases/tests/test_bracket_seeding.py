import pytest

from phases.services.finale_seeding import (
    ErreurSeeding,
    generer_paires_premier_tour,
)


import pytest

from phases.services.finale_seeding import (
    ErreurSeeding,
    generer_paires_premier_tour,
)


def test_seeding_4_equipes_demis():
    equipes = ["E1", "E2", "E3", "E4"]
    assert generer_paires_premier_tour(equipes) == [("E1", "E4"), ("E2", "E3")]


def test_seeding_8_equipes_quarts():
    equipes = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
    paires = generer_paires_premier_tour(equipes)
    assert len(paires) == 4
    assert all(a is not None and b is not None for a, b in paires)


def test_seeding_16_equipes_huitiemes():
    equipes = [f"E{i}" for i in range(1, 17)]
    paires = generer_paires_premier_tour(equipes)
    assert len(paires) == 8
    assert all(a is not None and b is not None for a, b in paires)


@pytest.mark.parametrize("n", [0, 1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 17])
def test_refuse_si_pas_4_8_16(n):
    equipes = [f"E{i}" for i in range(1, n + 1)]
    with pytest.raises(ErreurSeeding):
        generer_paires_premier_tour(equipes)

