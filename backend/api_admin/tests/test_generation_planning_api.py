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
from planning.models import Terrain


@pytest.mark.django_db
def test_admin_peut_generer_planning_phase_globale():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    # 8 terrains
    for i in range(4):
        Terrain.objects.create(edition=edition, nom=f"Int {i+1}", type_terrain="INTERIEUR", ordre=i)
    for i in range(4):
        Terrain.objects.create(
            edition=edition, nom=f"Ext {i+1}", type_terrain="EXTERIEUR", ordre=10 + i
        )

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sp = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    equipes = []
    for i in range(4):
        e = Equipe.objects.create(
            edition=edition,
            tournoi=tournoi,
            nom=f"E{i+1}",
            statut=StatutEquipe.VALIDEE,
        )
        equipes.append(e)
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    # Générer 6 matchs round-robin
    for i in range(4):
        for j in range(i + 1, 4):
            Match.objects.create(
                edition=edition,
                phase_globale=phase,
                sous_phase=sp,
                groupe=groupe,
                equipe_a=equipes[i],
                equipe_b=equipes[j],
                statut=StatutMatch.A_PLANIFIER,
            )

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.post(
        f"/api/admin/phases-globales/{phase.id}/generer-planning/", {}, format="json"
    )
    assert resp.status_code == 200

    assert Match.objects.filter(phase_globale=phase, terrain__isnull=False).count() == 6
    assert Match.objects.filter(phase_globale=phase, creneau__isnull=False).count() == 6


@pytest.mark.django_db
def test_non_admin_refuse_generation_planning():
    User = get_user_model()
    user = User.objects.create_user(username="user", password="pass", is_staff=False)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )

    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post(
        f"/api/admin/phases-globales/{phase.id}/generer-planning/", {}, format="json"
    )
    assert resp.status_code == 403
