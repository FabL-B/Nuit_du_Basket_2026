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
    assert fmt.nb_slots == 4


def test_format_bracket_quarts_si_entre_5_et_8():
    fmt = proposer_format_bracket(6)
    assert fmt.tour_depart == TourBracket.QUART_FINALE
    assert fmt.nb_slots == 8


def test_format_bracket_huitiemes_si_entre_9_et_16():
    fmt = proposer_format_bracket(12)
    assert fmt.tour_depart == TourBracket.HUITIEME_FINALE
    assert fmt.nb_slots == 16


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
    structure = generer_structure_bracket(6)

    assert len([m for m in structure if m.tour == TourBracket.QUART_FINALE]) == 4
    assert len([m for m in structure if m.tour == TourBracket.DEMI_FINALE]) == 2
    assert len([m for m in structure if m.tour == TourBracket.FINALE]) == 1


def test_generer_structure_huitiemes_produit_8_4_2_1():
    structure = generer_structure_bracket(12)

    assert len([m for m in structure if m.tour == TourBracket.HUITIEME_FINALE]) == 8
    assert len([m for m in structure if m.tour == TourBracket.QUART_FINALE]) == 4
    assert len([m for m in structure if m.tour == TourBracket.DEMI_FINALE]) == 2
    assert len([m for m in structure if m.tour == TourBracket.FINALE]) == 1
