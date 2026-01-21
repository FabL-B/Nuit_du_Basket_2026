import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import datetime

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from groupes.models import Groupe, GroupeEquipe
from inscriptions.models import Equipe, StatutEquipe

pytestmark = pytest.mark.django_db


def setup_tournoi_groupe():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE, libelle="Rookie")
    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    sp = SousPhase.objects.create(phase_globale=phase1, tournoi=tournoi, branche="A")

    g = Groupe.objects.create(sous_phase=sp, code="A1")

    e1 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE
    )
    e2 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE
    )

    GroupeEquipe.objects.create(groupe=g, equipe=e1, seed=1)
    GroupeEquipe.objects.create(groupe=g, equipe=e2, seed=2)

    return edition, tournoi, g


def test_public_tournois_accessible():
    client = APIClient()
    setup_tournoi_groupe()

    r = client.get("/api/public/tournois/", format="json")
    assert r.status_code == 200
    assert len(r.data) >= 1
    assert "code" in r.data[0]
    assert "code_display" in r.data[0]


def test_public_groupes_filter_by_tournoi():
    client = APIClient()
    setup_tournoi_groupe()

    r = client.get("/api/public/groupes/?tournoi=ROOKIE", format="json")
    assert r.status_code == 200
    assert all(item["tournoi"] == "ROOKIE" for item in r.data)


def test_public_groupe_detail_includes_equipes():
    client = APIClient()
    _, _, g = setup_tournoi_groupe()

    r = client.get(f"/api/public/groupes/{g.id}/", format="json")
    assert r.status_code == 200
    assert "equipes" in r.data
    assert len(r.data["equipes"]) == 2
    assert "nom" in r.data["equipes"][0]
