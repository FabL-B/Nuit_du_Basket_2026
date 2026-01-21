import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from core.models import Edition
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, StatutEquipe
from planning.models import Terrain
from planning.services_planning import ErreurGenerationPlanning

pytestmark = pytest.mark.django_db


def mk_admin():
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )


def setup_phase1_complete():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)

    # Terrains requis
    for i in range(8):
        Terrain.objects.create(
            edition=edition,
            nom=f"T{i+1}",
            ordre=i + 1,
            est_actif=True,
        )

    # 8 équipes minimum
    for i in range(8):
        Equipe.objects.create(
            edition=edition,
            tournoi=tournoi,
            nom=f"E{i+1}",
            statut=StatutEquipe.VALIDEE,
        )

    return edition, phase1


def rendre_phase1_planifiable(client, phase1):
    # sous-phases
    r_sp = client.post(
        f"/api/admin/phases-globales/{phase1.id}/generer-sous-phases/", data={}, format="json"
    )
    assert r_sp.status_code == 200

    # groupes
    sp_id = SousPhase.objects.get(
        phase_globale=phase1,
        tournoi__code=CodeTournoi.ROOKIE,
    ).id
    r_g = client.post(
        f"/api/admin/sous-phases/{sp_id}/generer-groupes-phase1/", data={}, format="json"
    )
    assert r_g.status_code == 200

    # matchs
    r_m = client.post(
        f"/api/admin/phases-globales/{phase1.id}/generer-matchs/", data={}, format="json"
    )
    assert r_m.status_code == 200


def test_planning_global_refuse_regeneration():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    edition, phase1 = setup_phase1_complete()
    rendre_phase1_planifiable(client, phase1)

    payload = {
        "phase1_id": phase1.id,
        "phase2_id": None,
        "phase_finale_id": None,
    }

    # 1er appel → OK
    r1 = client.post(
        f"/api/admin/editions/{edition.id}/planning-global/generer/",
        data=payload,
        format="json",
    )
    assert r1.status_code == 200, r1.data

    # 2e appel → refus
    r2 = client.post(
        f"/api/admin/editions/{edition.id}/planning-global/generer/",
        data=payload,
        format="json",
    )
    assert r2.status_code == 400, r2.data

    msg = str(r2.data)
    assert "déjà" in msg.lower() or "planifi" in msg.lower()
