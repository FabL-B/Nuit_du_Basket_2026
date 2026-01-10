import pytest

from phases.services.finale_bracket import (
    ErreurBracket,
    proposer_format_bracket,
    generer_structure_bracket,
    TourBracket,
)


def test_format_bracket_minimum_demis_si_4_equipes():
    fmt = proposer_format_bracket(4)
    assert fmt.tour_depart == TourBracket.DEMI_FINALE
    assert fmt.nb_equipes == 4
    assert fmt.nb_matchs_premier_tour == 2


@pytest.mark.parametrize("n", [5, 6, 7, 9, 10, 11, 12, 13, 14, 15])
def test_format_bracket_refuse_tailles_intermediaires(n):
    with pytest.raises(ErreurBracket):
        proposer_format_bracket(n)


def test_refuse_moins_de_4_equipes():
    with pytest.raises(ErreurBracket):
        proposer_format_bracket(3)


def test_refuse_plus_de_16_equipes():
    with pytest.raises(ErreurBracket):
        proposer_format_bracket(17)


def test_generer_structure_demis_produit_2_demis_et_1_finale():
    structure = generer_structure_bracket(4)

    assert [m.tour for m in structure] == [
        TourBracket.DEMI_FINALE,
        TourBracket.DEMI_FINALE,
        TourBracket.FINALE,
    ]

    demis = [m for m in structure if m.tour == TourBracket.DEMI_FINALE]
    finale = [m for m in structure if m.tour == TourBracket.FINALE]

    assert len(demis) == 2
    assert len(finale) == 1

    # finale dépend des deux demis
    assert finale[0].depuis_match_ids == [demis[0].id, demis[1].id]


def test_generer_structure_quarts_produit_4_quarts_2_demis_1_finale():
    structure = generer_structure_bracket(8)
    assert sum(1 for m in structure if m.tour == TourBracket.QUART_FINALE) == 4
    assert sum(1 for m in structure if m.tour == TourBracket.DEMI_FINALE) == 2
    assert sum(1 for m in structure if m.tour == TourBracket.FINALE) == 1


def test_generer_structure_huitiemes_produit_8_4_2_1():
    structure = generer_structure_bracket(16)
    assert sum(1 for m in structure if m.tour == TourBracket.HUITIEME_FINALE) == 8
    assert sum(1 for m in structure if m.tour == TourBracket.QUART_FINALE) == 4
    assert sum(1 for m in structure if m.tour == TourBracket.DEMI_FINALE) == 2
    assert sum(1 for m in structure if m.tour == TourBracket.FINALE) == 1
