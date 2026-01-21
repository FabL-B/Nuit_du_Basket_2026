import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from core.models import Edition
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, StatutEquipe
from planning.models import Terrain


pytestmark = pytest.mark.django_db


def mk_admin():
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )


def test_planning_global_generer_ok():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    # Terrains requis par le planning (au moins 1, en pratique 8)
    for i in range(8):
        Terrain.objects.create(
            edition=edition,
            nom=f"T{i+1}",
            ordre=i + 1,
            est_actif=True,
        )

    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)

    # 8 équipes minimum pour phase 1
    for i in range(8):
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )

    # Sous-phases
    r_sp = client.post(
        f"/api/admin/phases-globales/{phase1.id}/generer-sous-phases/", data={}, format="json"
    )
    assert r_sp.status_code == 200, r_sp.data

    # Groupes (rookie)
    sous_phase_id = SousPhase.objects.get(phase_globale=phase1, tournoi__code=CodeTournoi.ROOKIE).id
    r_g = client.post(
        f"/api/admin/sous-phases/{sous_phase_id}/generer-groupes-phase1/", data={}, format="json"
    )
    assert r_g.status_code == 200, r_g.data

    # Matchs
    r_m = client.post(
        f"/api/admin/phases-globales/{phase1.id}/generer-matchs/", data={}, format="json"
    )
    assert r_m.status_code == 200, r_m.data

    # Planning global (sans phase2/finale pour commencer)
    payload = {
        "phase1_id": phase1.id,
        "phase2_id": None,
        "phase_finale_id": None,
        "heure_debut_concours": "18:00",
        "duree_concours_minutes": 90,
    }
    r = client.post(
        f"/api/admin/editions/{edition.id}/planning-global/generer/", data=payload, format="json"
    )
    assert r.status_code == 200, r.data
    assert r.data["edition_id"] == edition.id
    assert "resume" in r.data
