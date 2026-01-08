from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from groupes.models import Groupe, GroupeEquipe
from inscriptions.models import Equipe, StatutEquipe


@pytest.mark.django_db
def test_admin_peut_lister_et_detail_groupes_avec_equipes():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)

    g1 = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)
    GroupeEquipe.objects.create(groupe=g1, equipe=e1)
    GroupeEquipe.objects.create(groupe=g1, equipe=e2)

    client = APIClient()
    client.force_authenticate(user=admin)

    # list
    resp = client.get("/api/admin/groupes/")
    assert resp.status_code == 200

    data = resp.data["results"] if isinstance(resp.data, dict) and "results" in resp.data else resp.data
    assert len(data) == 1

    # detail
    resp2 = client.get(f"/api/admin/groupes/{g1.id}/")
    assert resp2.status_code == 200
    assert resp2.data["code"] == "A"
    assert len(resp2.data["equipes"]) == 2


@pytest.mark.django_db
def test_admin_peut_supprimer_groupe():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)

    g1 = Groupe.objects.create(sous_phase=sp, code="A")

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.delete(f"/api/admin/groupes/{g1.id}/")
    assert resp.status_code in (204, 200)

    assert Groupe.objects.filter(id=g1.id).exists() is False
