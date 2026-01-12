import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase

pytestmark = pytest.mark.django_db


def mk_user():
    User = get_user_model()
    # utilisateur normal (non admin)
    return User.objects.create_user(username="user", email="user@test.com", password="user123")


def setup_minimal():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    sous_phase = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche="A")
    return edition, phase, sous_phase


@pytest.mark.parametrize(
    "method,url_builder",
    [
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/generer-sous-phases/"),
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/generer-matchs/"),
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/generer-planning/"),
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/cloturer/"),
        ("get",  lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/phase2-preview/"),
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/phase2-generer/"),
        ("post", lambda edition, phase, sp: f"/api/admin/sous-phases/{sp.id}/generer-groupes-phase1/"),
        ("post", lambda edition, phase, sp: f"/api/admin/editions/{edition.id}/planning-global/generer/"),
    ],
)
def test_admin_endpoints_refuse_non_admin(method, url_builder):
    user = mk_user()
    client = APIClient()
    client.force_authenticate(user)

    edition, phase, sp = setup_minimal()
    url = url_builder(edition, phase, sp)

    if method == "get":
        resp = client.get(url)
    else:
        # payload minimal : on s'en fiche, la permission doit bloquer avant
        resp = client.post(url, data={}, format="json")

    assert resp.status_code == 403, getattr(resp, "data", resp.content)


@pytest.mark.parametrize(
    "method,url_builder",
    [
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/generer-sous-phases/"),
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/generer-matchs/"),
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/generer-planning/"),
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/cloturer/"),
        ("get",  lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/phase2-preview/"),
        ("post", lambda edition, phase, sp: f"/api/admin/phases-globales/{phase.id}/phase2-generer/"),
        ("post", lambda edition, phase, sp: f"/api/admin/sous-phases/{sp.id}/generer-groupes-phase1/"),
        ("post", lambda edition, phase, sp: f"/api/admin/editions/{edition.id}/planning-global/generer/"),
    ],
)
def test_admin_endpoints_refuse_anonyme(method, url_builder):
    client = APIClient()
    edition, phase, sp = setup_minimal()
    url = url_builder(edition, phase, sp)

    if method == "get":
        resp = client.get(url)
    else:
        resp = client.post(url, data={}, format="json")

    # Selon ta config DRF, ça peut être 401 (souvent) ou 403.
    assert resp.status_code in (401, 403), getattr(resp, "data", resp.content)
