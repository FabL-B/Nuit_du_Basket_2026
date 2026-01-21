import pytest
from django.utils import timezone
from datetime import timedelta, date

from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from groupes.models import Groupe
from inscriptions.models import Equipe, StatutEquipe
from planning.models import Terrain, Creneau
from matchs.models import Match

pytestmark = pytest.mark.django_db


def setup_planning():
    edition = Edition.objects.create(
        nom="NDB 2026", date_evenement=date(2026, 6, 20), duree_creneau_minutes=15
    )
    terrain = Terrain.objects.create(edition=edition, nom="Terrain 1", ordre=1, est_actif=True)

    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    sp = SousPhase.objects.create(phase_globale=phase1, tournoi=tournoi, branche="A")
    g = Groupe.objects.create(sous_phase=sp, code="A1")

    e1 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE
    )
    e2 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE
    )
    e3 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E3", statut=StatutEquipe.VALIDEE
    )
    e4 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E4", statut=StatutEquipe.VALIDEE
    )

    now = timezone.now()

    c_past = Creneau.objects.create(
        edition=edition, index=1, debut=now - timedelta(minutes=30), duree_minutes=15
    )
    c_now = Creneau.objects.create(
        edition=edition, index=2, debut=now - timedelta(minutes=5), duree_minutes=15
    )
    c_future = Creneau.objects.create(
        edition=edition, index=3, debut=now + timedelta(minutes=30), duree_minutes=15
    )

    m_past = Match.objects.create(
        edition=edition,
        phase_globale=phase1,
        sous_phase=sp,
        groupe=g,
        equipe_a=e1,
        equipe_b=e2,
        creneau=c_past,
        terrain=terrain,
    )
    m_now = Match.objects.create(
        edition=edition,
        phase_globale=phase1,
        sous_phase=sp,
        groupe=g,
        equipe_a=e1,
        equipe_b=e3,
        creneau=c_now,
        terrain=terrain,
    )
    m_future = Match.objects.create(
        edition=edition,
        phase_globale=phase1,
        sous_phase=sp,
        groupe=g,
        equipe_a=e1,
        equipe_b=e4,
        creneau=c_future,
        terrain=terrain,
    )

    return edition, e1, (m_past.id, m_now.id, m_future.id)


def test_public_planning_status_filters_and_statut_field():
    client = APIClient()
    edition, e1, (m_past, m_now, m_future) = setup_planning()

    r = client.get(f"/api/public/planning/?edition={edition.id}&status=en_cours", format="json")
    assert r.status_code == 200
    ids = {item["match_id"] for item in r.data}
    assert m_now in ids
    assert all(item["statut"] == "EN_COURS" for item in r.data)

    r = client.get(f"/api/public/planning/?edition={edition.id}&status=a_venir", format="json")
    assert r.status_code == 200
    ids = {item["match_id"] for item in r.data}
    assert m_future in ids
    assert all(item["statut"] == "A_VENIR" for item in r.data)

    r = client.get(f"/api/public/planning/?edition={edition.id}&status=termines", format="json")
    assert r.status_code == 200
    ids = {item["match_id"] for item in r.data}
    assert m_past in ids
    assert all(item["statut"] == "TERMINE" for item in r.data)

    # filtre equipe
    r = client.get(f"/api/public/planning/?edition={edition.id}&equipe={e1.id}", format="json")
    assert r.status_code == 200
    assert len(r.data) >= 3

    # limit
    r = client.get(f"/api/public/planning/?edition={edition.id}&limit=2", format="json")
    assert r.status_code == 200
    assert len(r.data) == 2
