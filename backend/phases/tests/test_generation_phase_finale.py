import pytest

from phases.services.finale_bracket import ErreurBracket, generer_structure_bracket


@pytest.mark.parametrize("n", [0, 1, 2, 3, 5, 6, 7, 9, 15, 17])
def test_finale_refuse_taille_invalide(n):
    with pytest.raises(ErreurBracket):
        generer_structure_bracket(nb_equipes=n)


@pytest.mark.parametrize("n, total_matchs_attendus", [(4, 3), (8, 7), (16, 15)])
def test_finale_genere_structure_complete(n, total_matchs_attendus):
    structure = generer_structure_bracket(nb_equipes=n)
    assert len(structure) == total_matchs_attendus


@pytest.mark.parametrize(
    "n, nb_premier_tour, nb_tours",
    [
        (4, 2, 2),  # demis + finale
        (8, 4, 3),  # quarts + demis + finale
        (16, 8, 4),  # 8e + quarts + demis + finale
    ],
)
def test_finale_structure_dependances(n, nb_premier_tour, nb_tours):
    structure = generer_structure_bracket(nb_equipes=n)

    # Les nb_premier_tour premiers matchs doivent ne dépendre de rien
    premiers = structure[:nb_premier_tour]
    assert all(m.depuis_match_ids == [] for m in premiers)

    # Tous les matchs suivants doivent dépendre exactement de 2 matchs
    suivants = structure[nb_premier_tour:]
    assert all(len(m.depuis_match_ids) == 2 for m in suivants)

    # Les IDs référencés doivent exister et être antérieurs dans la liste
    index_par_id = {m.id: idx for idx, m in enumerate(structure)}
    for idx, m in enumerate(structure):
        for dep_id in m.depuis_match_ids:
            assert dep_id in index_par_id
            assert index_par_id[dep_id] < idx

    # Contrôle simple du nombre de tours présents
    tours = [m.tour for m in structure]
    assert len(set(tours)) == nb_tours


def test_finale_match_final_unique_et_depend_de_2_matchs():
    structure = generer_structure_bracket(nb_equipes=8)

    # Dans ta génération, la finale est le dernier match
    finale = structure[-1]
    assert len(finale.depuis_match_ids) == 2

    # Ses deux dépendances doivent exister
    ids = {m.id for m in structure}
    assert finale.depuis_match_ids[0] in ids
    assert finale.depuis_match_ids[1] in ids
