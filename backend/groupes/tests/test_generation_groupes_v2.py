from datetime import date

import pytest

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import GroupeEquipe
from groupes.services import generer_groupes_pour_sous_phase, ErreurGenerationGroupes


def _setup_sous_phase():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sous_phase = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    return edition, tournoi, sous_phase


def _creer_equipes(edition, tournoi, n: int):
    for i in range(n):
        Equipe.objects.create(
            edition=edition,
            tournoi=tournoi,
            nom=f"Equipe {i}",
            statut=StatutEquipe.VALIDEE,
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "n, tailles_attendues",
    [
        (8,  [4, 4]),
        (9,  [4, 5]),
        (10, [5, 5]),
        (12, [4, 4, 4]),
        (13, [4, 4, 5]),
        (14, [4, 5, 5]),
        (15, [5, 5, 5]),
        (16, [4, 4, 4, 4]),
    ],
)
def test_generation_groupes_regles_v2(n, tailles_attendues):
    edition, tournoi, sous_phase = _setup_sous_phase()
    _creer_equipes(edition, tournoi, n)

    groupes = generer_groupes_pour_sous_phase(sous_phase)

    tailles = sorted(g.equipes.count() for g in groupes)
    assert tailles == sorted(tailles_attendues)

    # sécurité: aucune taille 3
    assert all(t in {4, 5} for t in tailles)

    # toutes les équipes affectées une fois
    assert GroupeEquipe.objects.filter(groupe__sous_phase=sous_phase).count() == n


@pytest.mark.django_db
@pytest.mark.parametrize("n", [0, 1, 2, 3, 4, 5, 6, 7])
def test_generation_refuse_moins_de_8(n):
    edition, tournoi, sous_phase = _setup_sous_phase()
    _creer_equipes(edition, tournoi, n)

    with pytest.raises(ErreurGenerationGroupes):
        generer_groupes_pour_sous_phase(sous_phase)


@pytest.mark.django_db
def test_generation_refuse_11():
    edition, tournoi, sous_phase = _setup_sous_phase()
    _creer_equipes(edition, tournoi, 11)

    with pytest.raises(ErreurGenerationGroupes):
        generer_groupes_pour_sous_phase(sous_phase)


@pytest.mark.django_db
def test_generation_refuse_si_groupes_deja_existants():
    edition, tournoi, sous_phase = _setup_sous_phase()
    _creer_equipes(edition, tournoi, 8)

    generer_groupes_pour_sous_phase(sous_phase)

    with pytest.raises(ErreurGenerationGroupes):
        generer_groupes_pour_sous_phase(sous_phase)
