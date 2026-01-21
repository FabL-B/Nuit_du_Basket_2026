import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from core.models import Edition
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import GroupeEquipe, Groupe


pytestmark = pytest.mark.django_db


def mk_admin():
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )


def setup_sous_phase_phase1():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    sous_phase = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche="A"
    )  # adapte branche
    return edition, tournoi, phase, sous_phase


def test_generer_groupes_phase1_ok():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    edition, tournoi, _, sous_phase = setup_sous_phase_phase1()

    # Minimum métier : 8 équipes requises pour générer les groupes phase 1
    for i in range(8):
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )

    url = f"/api/admin/sous-phases/{sous_phase.id}/generer-groupes-phase1/"
    r1 = client.post(url, data={}, format="json")
    assert r1.status_code == 200
    assert r1.data["created"] is True

    assert Groupe.objects.filter(sous_phase=sous_phase).exists()
    assert GroupeEquipe.objects.filter(groupe__sous_phase=sous_phase).exists()
