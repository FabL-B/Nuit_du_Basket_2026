import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from core.models import Edition
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from tournois.models import Tournoi, CodeTournoi


pytestmark = pytest.mark.django_db


def mk_admin():
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )  # adapte champs


def mk_edition():
    return Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")


def mk_phase1(edition):
    return PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)


def mk_tournois(edition):
    # selon ton modèle tournoi : au minimum edition + code
    Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.COMPETITEUR)


def test_generer_sous_phases_cree_et_est_idempotent():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    edition = mk_edition()
    mk_tournois(edition)
    phase = mk_phase1(edition)

    url = f"/api/admin/phases-globales/{phase.id}/generer-sous-phases/"

    # 1er appel : crée
    r1 = client.post(url, data={}, format="json")
    assert r1.status_code == 200
    assert r1.data["created"] is True
    assert r1.data["sous_phases_creees"] > 0

    total_after_1 = SousPhase.objects.filter(phase_globale=phase).count()
    assert total_after_1 == r1.data["sous_phases_creees"]
    assert len(r1.data["sous_phase_ids"]) == total_after_1

    # 2e appel : idempotent (pas de doublon)
    r2 = client.post(url, data={}, format="json")
    assert r2.status_code == 400
    assert "sous-phases existent déjà" in r2.data["detail"].lower()

    total_after_2 = SousPhase.objects.filter(phase_globale=phase).count()
    assert total_after_2 == total_after_1
