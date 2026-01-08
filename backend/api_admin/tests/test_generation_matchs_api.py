from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from groupes.models import Groupe, GroupeEquipe
from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match


@pytest.mark.django_db
def test_admin_peut_generer_matchs_pour_phase_globale():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    # 4 équipes => round-robin => 6 matchs attendus
    equipes = []
    for i in range(4):
        e = Equipe.objects.create(edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE)
        equipes.append(e)
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.post(f"/api/admin/phases-globales/{phase.id}/generer-matchs/", {}, format="json")
    assert resp.status_code == 200

    assert Match.objects.filter(phase_globale=phase).count() == 6


@pytest.mark.django_db
def test_non_admin_refuse_generation_matchs():
    User = get_user_model()
    user = User.objects.create_user(username="user", password="pass", is_staff=False)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)

    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post(f"/api/admin/phases-globales/{phase.id}/generer-matchs/", {}, format="json")
    assert resp.status_code == 403
