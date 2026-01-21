import pytest
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase, BrancheSousPhase
from groupes.models import Groupe, GroupeEquipe
from inscriptions.models import Equipe, StatutEquipe
from classements.models import Classement


pytestmark = pytest.mark.django_db


def setup_groupe_et_classement():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    g = Groupe.objects.create(sous_phase=sp, code="A1")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)
    e3 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E3", statut=StatutEquipe.VALIDEE)

    GroupeEquipe.objects.create(groupe=g, equipe=e1)
    GroupeEquipe.objects.create(groupe=g, equipe=e2)
    GroupeEquipe.objects.create(groupe=g, equipe=e3)

    # points_classement + difference + points_marques => ordre attendu: e2 > e1 > e3
    Classement.objects.create(groupe=g, equipe=e1, points_classement=6, difference=5, points_marques=30)
    Classement.objects.create(groupe=g, equipe=e2, points_classement=6, difference=10, points_marques=25)
    Classement.objects.create(groupe=g, equipe=e3, points_classement=3, difference=-2, points_marques=10)

    return edition, g


def test_public_groupe_classement_detail_ordered():
    client = APIClient()
    _, g = setup_groupe_et_classement()

    r = client.get(f"/api/public/groupes/{g.id}/classement/")
    assert r.status_code == 200, r.data

    rows = r.data["rows"]
    assert [row["equipe"] for row in rows] == ["E2", "E1", "E3"]
    assert [row["rang"] for row in rows] == [1, 2, 3]


def test_public_groupes_classements_resume_top():
    client = APIClient()
    edition, g = setup_groupe_et_classement()

    r = client.get(f"/api/public/groupes/classements/?edition={edition.id}&resume=true&top=2")
    assert r.status_code == 200, r.data

    assert len(r.data) == 1
    assert len(r.data[0]["rows"]) == 2
    assert [row["equipe"] for row in r.data[0]["rows"]] == ["E2", "E1"]
