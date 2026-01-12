import pytest
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from inscriptions.models import Equipe, StatutEquipe
from planning.models import Terrain, Creneau
from matchs.models import Match, Score
from django.utils import timezone
from datetime import datetime

pytestmark = pytest.mark.django_db


def setup_resultats_minimal():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)

    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    sous_phase = SousPhase.objects.create(phase_globale=phase1, tournoi=tournoi, branche="A")

    terrain = Terrain.objects.create(edition=edition, nom="T1", ordre=1, est_actif=True)
    debut = timezone.make_aware(datetime(2026, 6, 20, 14, 0))
    creneau = Creneau.objects.create(edition=edition, index=1, debut=debut)

    equipe_a = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    equipe_b = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)

    match = Match.objects.create(
        edition=edition,
        phase_globale=phase1,
        sous_phase=sous_phase,
        groupe=None,
        equipe_a=equipe_a,
        equipe_b=equipe_b,
        creneau=creneau,
        terrain=terrain,
    )

    Score.objects.create(match=match, points_a=10, points_b=8)
    return edition


def test_public_resultats_only_matches_with_score():
    client = APIClient()
    setup_resultats_minimal()

    r = client.get("/api/public/resultats/", format="json")
    assert r.status_code == 200
    assert len(r.data) >= 1
    assert r.data[0]["score"] is not None
