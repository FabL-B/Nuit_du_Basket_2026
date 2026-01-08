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
def test_admin_peut_declarer_forfait_a():
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

    match = Match.objects.create(
        edition=edition,
        phase_globale=phase,
        sous_phase=sp,
        groupe=groupe,
        equipe_a=e1,
        equipe_b=e2,
        statut=StatutMatch.PLANIFIE,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.post(f"/api/admin/matchs/{match.id}/forfait/", {"statut": StatutMatch.FORFAIT_A}, format="json")
    assert resp.status_code == 200

    match.refresh_from_db()
    assert match.statut == StatutMatch.FORFAIT_A


@pytest.mark.django_db
def test_forfait_refuse_si_match_termine():
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

    match = Match.objects.create(
        edition=edition,
        phase_globale=phase,
        sous_phase=sp,
        groupe=groupe,
        equipe_a=e1,
        equipe_b=e2,
        statut=StatutMatch.TERMINE,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.post(f"/api/admin/matchs/{match.id}/forfait/", {"statut": StatutMatch.FORFAIT_A}, format="json")
    assert resp.status_code == 400
