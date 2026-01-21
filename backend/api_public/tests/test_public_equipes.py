import pytest
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, Joueur, StatutEquipe
from groupes.models import Groupe, GroupeEquipe
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase, BrancheSousPhase


pytestmark = pytest.mark.django_db


def setup_equipes():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)
    e3 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E3", statut=StatutEquipe.BROUILLON)

    Joueur.objects.create(equipe=e1, prenom="A", nom="AA")
    Joueur.objects.create(equipe=e1, prenom="B", nom="BB")

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    g = Groupe.objects.create(sous_phase=sp, code="A1")
    GroupeEquipe.objects.create(groupe=g, equipe=e1)

    return edition, tournoi, g, e1, e2, e3


def test_public_equipes_list_filters_and_excludes_brouillon():
    client = APIClient()
    edition, tournoi, g, e1, e2, e3 = setup_equipes()

    r = client.get(f"/api/public/equipes/?edition={edition.id}&tournoi={tournoi.code}")
    assert r.status_code == 200

    names = [x["nom"] for x in r.data]
    assert "E1" in names
    assert "E2" in names
    assert "E3" not in names  # exclu car BROUILLON


def test_public_equipes_list_filter_by_groupe():
    client = APIClient()
    edition, tournoi, g, e1, e2, e3 = setup_equipes()

    r = client.get(f"/api/public/equipes/?edition={edition.id}&groupe={g.id}")
    assert r.status_code == 200
    assert [x["nom"] for x in r.data] == ["E1"]


def test_public_equipes_detail_includes_joueurs():
    client = APIClient()
    edition, tournoi, g, e1, e2, e3 = setup_equipes()

    r = client.get(f"/api/public/equipes/{e1.id}/")
    assert r.status_code == 200
    assert r.data["nom"] == "E1"
    assert len(r.data["joueurs"]) == 2
