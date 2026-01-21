import pytest
from datetime import date, timedelta
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from groupes.models import Groupe
from inscriptions.models import Equipe, StatutEquipe
from planning.models import Terrain, Creneau
from matchs.models import Match
from matchs.models import Score
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def setup_resultats():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20), duree_creneau_minutes=15)
    terrain = Terrain.objects.create(edition=edition, nom="Terrain 1", ordre=1, est_actif=True)

    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    sp = SousPhase.objects.create(phase_globale=phase1, tournoi=tournoi, branche="A")
    g = Groupe.objects.create(sous_phase=sp, code="A1")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)

    now = timezone.now()
    c = Creneau.objects.create(edition=edition, index=1, debut=now - timedelta(minutes=30), duree_minutes=15)

    m = Match.objects.create(
        edition=edition, phase_globale=phase1, sous_phase=sp, groupe=g,
        equipe_a=e1, equipe_b=e2, creneau=c, terrain=terrain
    )

    User = get_user_model()
    u = User.objects.create_user(username="u1", email="u1@test.com", password="x")

    Score.objects.create(
        match=m,
        points_a=21,
        points_b=17,
        valide_le=now,
        valide_par=u,
    )
    return edition, tournoi, g, e1, m.id


def test_public_resultats_filters():
    client = APIClient()
    edition, tournoi, g, e1, mid = setup_resultats()

    r = client.get(f"/api/public/resultats/?edition={edition.id}", format="json")
    assert r.status_code == 200
    assert any(item["match_id"] == mid for item in r.data)

    r = client.get(f"/api/public/resultats/?edition={edition.id}&categorie={tournoi.code}&groupe={g.id}", format="json")
    assert r.status_code == 200
    assert any(item["match_id"] == mid for item in r.data)

    r = client.get(f"/api/public/resultats/?edition={edition.id}&equipe={e1.id}", format="json")
    assert r.status_code == 200
    assert any(item["match_id"] == mid for item in r.data)

    r = client.get(f"/api/public/resultats/?edition={edition.id}&limit=1", format="json")
    assert r.status_code == 200
    assert len(r.data) == 1
