from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from groupes.models import Groupe, GroupeEquipe
from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match, StatutMatch


@pytest.mark.django_db
def test_non_admin_refuse_matchs_list():
    User = get_user_model()
    user = User.objects.create_user(username="user", password="pass", is_staff=False)

    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/admin/matchs/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_admin_peut_lister_matchs():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)
    GroupeEquipe.objects.create(groupe=groupe, equipe=e1)
    GroupeEquipe.objects.create(groupe=groupe, equipe=e2)

    Match.objects.create(
        edition=edition,
        phase_globale=phase,
        sous_phase=sp,
        groupe=groupe,
        equipe_a=e1,
        equipe_b=e2,
        statut=StatutMatch.A_PLANIFIER,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.get("/api/admin/matchs/")
    assert resp.status_code == 200

    data = resp.data["results"] if isinstance(resp.data, dict) and "results" in resp.data else resp.data
    assert len(data) == 1
    assert data[0]["equipe_a_nom"] == "E1"
