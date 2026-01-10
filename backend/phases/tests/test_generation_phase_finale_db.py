import pytest
from datetime import date

from django.contrib.auth import get_user_model

from core.models import Edition
from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match, StatutMatch
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from tournois.models import Tournoi, CodeTournoi

from phases.services.finale_db import (
    ErreurPhaseFinaleDB,
    generer_matchs_phase_finale,
)


def _setup_base():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase_finale = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.FINALE, sequence=1
    )
    sp_finale = SousPhase.objects.create(
        phase_globale=phase_finale,
        tournoi=tournoi,
        branche=BrancheSousPhase.CHALLENGE,
    )
    return edition, tournoi, phase_finale, sp_finale


@pytest.mark.django_db
@pytest.mark.parametrize("n", [0, 1, 2, 3, 5, 6, 7, 9, 15, 17])
def test_finale_db_refuse_taille_invalide(n):
    edition, tournoi, phase_finale, sp_finale = _setup_base()

    equipes = [
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )
        for i in range(max(n, 1))
    ]
    ids = [e.id for e in equipes[:n]]

    with pytest.raises(ErreurPhaseFinaleDB):
        generer_matchs_phase_finale(phase_finale, sp_finale, ids)


@pytest.mark.django_db
def test_finale_db_refuse_doublons():
    edition, tournoi, phase_finale, sp_finale = _setup_base()

    equipes = [
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )
        for i in range(4)
    ]
    ids = [equipes[0].id, equipes[1].id, equipes[1].id, equipes[2].id]

    with pytest.raises(ErreurPhaseFinaleDB):
        generer_matchs_phase_finale(phase_finale, sp_finale, ids)


@pytest.mark.django_db
def test_finale_db_refuse_si_equipe_autre_edition():
    edition, tournoi, phase_finale, sp_finale = _setup_base()

    autre = Edition.objects.create(nom="NDB 2027", date_evenement=date(2027, 6, 20))
    tournoi_autre = Tournoi.objects.create(edition=autre, code=CodeTournoi.LOISIR)

    equipes_ok = [
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )
        for i in range(3)
    ]
    e_bad = Equipe.objects.create(
        edition=autre, tournoi=tournoi_autre, nom="BAD", statut=StatutEquipe.VALIDEE
    )

    ids = [e.id for e in equipes_ok] + [e_bad.id]

    with pytest.raises(ErreurPhaseFinaleDB):
        generer_matchs_phase_finale(phase_finale, sp_finale, ids)


@pytest.mark.django_db
def test_finale_db_refuse_si_equipe_autre_tournoi():
    edition, tournoi, phase_finale, sp_finale = _setup_base()

    tournoi2 = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)

    equipes_ok = [
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )
        for i in range(3)
    ]
    e_bad = Equipe.objects.create(
        edition=edition, tournoi=tournoi2, nom="BAD", statut=StatutEquipe.VALIDEE
    )

    ids = [e.id for e in equipes_ok] + [e_bad.id]

    with pytest.raises(ErreurPhaseFinaleDB):
        generer_matchs_phase_finale(phase_finale, sp_finale, ids)


@pytest.mark.django_db
@pytest.mark.parametrize("n, matchs_attendus", [(4, 2), (8, 4), (16, 8)])
def test_finale_db_cree_matchs_premier_tour_uniquement(n, matchs_attendus):
    edition, tournoi, phase_finale, sp_finale = _setup_base()

    equipes = [
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )
        for i in range(n)
    ]
    ids = [e.id for e in equipes]

    resume = generer_matchs_phase_finale(phase_finale, sp_finale, ids)
    assert resume.matchs_crees == matchs_attendus

    qs = Match.objects.filter(phase_globale=phase_finale, sous_phase=sp_finale).order_by("id")
    assert qs.count() == matchs_attendus
    assert all(m.groupe_id is None for m in qs)
    assert all(m.creneau_id is None for m in qs)
    assert all(m.terrain_id is None for m in qs)
    assert all(m.statut == StatutMatch.A_PLANIFIER for m in qs)


@pytest.mark.django_db
def test_finale_db_refuse_si_matchs_deja_existants():
    edition, tournoi, phase_finale, sp_finale = _setup_base()

    equipes = [
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )
        for i in range(4)
    ]
    ids = [e.id for e in equipes]

    generer_matchs_phase_finale(phase_finale, sp_finale, ids)

    with pytest.raises(ErreurPhaseFinaleDB):
        generer_matchs_phase_finale(phase_finale, sp_finale, ids)
