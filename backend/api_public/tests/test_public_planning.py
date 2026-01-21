import pytest
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from inscriptions.models import Equipe, StatutEquipe
from planning.models import Terrain
from matchs.models import Match

pytestmark = pytest.mark.django_db


def setup_planning_public_minimal():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)

    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    sous_phase = SousPhase.objects.create(phase_globale=phase1, tournoi=tournoi, branche="A")

    terrain = Terrain.objects.create(edition=edition, nom="T1", ordre=1, est_actif=True)

    # 2 équipes + 1 match déjà planifié (on évite de dépendre des services admin)
    equipe_a = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE
    )
    equipe_b = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE
    )

    # Crée un créneau minimal (adapte si ton modèle Creneau exige autre chose)
    from planning.models import Creneau

    creneau = Creneau.objects.create(edition=edition, index=1, debut="2026-06-20T14:00:00Z")

    Match.objects.create(
        edition=edition,
        phase_globale=phase1,
        sous_phase=sous_phase,
        groupe=None,
        equipe_a=equipe_a,
        equipe_b=equipe_b,
        creneau=creneau,
        terrain=terrain,
    )

    return edition


def test_public_planning_is_accessible_without_auth():
    client = APIClient()
    edition = setup_planning_public_minimal()

    r = client.get("/api/public/planning/", format="json")
    assert r.status_code == 200
    assert isinstance(r.data, list)
    assert len(r.data) >= 1
    assert "terrain" in r.data[0]
    assert "equipe_a" in r.data[0]


def test_public_planning_filter_by_tournoi():
    client = APIClient()
    setup_planning_public_minimal()

    r = client.get("/api/public/planning/?tournoi=ROOKIE", format="json")
    assert r.status_code == 200
    assert all(item["tournoi"] == "ROOKIE" for item in r.data)
