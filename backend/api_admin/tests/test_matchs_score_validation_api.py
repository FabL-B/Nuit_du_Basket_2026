from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from groupes.models import Groupe, GroupeEquipe
from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match, StatutMatch, Score


@pytest.mark.django_db
def test_admin_peut_valider_score_et_termine_match():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sp = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE
    )
    e2 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE
    )
    GroupeEquipe.objects.create(groupe=groupe, equipe=e1)
    GroupeEquipe.objects.create(groupe=groupe, equipe=e2)

    match = Match.objects.create(
        edition=edition,
        phase_globale=phase,
        sous_phase=sp,
        groupe=groupe,
        equipe_a=e1,
        equipe_b=e2,
        statut=StatutMatch.A_PLANIFIER,
    )

    # score saisi
    Score.objects.create(match=match, points_a=10, points_b=8)

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.post(f"/api/admin/matchs/{match.id}/score/valider/", {}, format="json")
    assert resp.status_code == 200

    match.refresh_from_db()
    assert match.statut == StatutMatch.TERMINE

    score = Score.objects.get(match=match)
    assert score.valide_le is not None
    assert score.valide_par_id == admin.id


@pytest.mark.django_db
def test_admin_refuse_valider_si_pas_de_score():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sp = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE
    )
    e2 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE
    )
    GroupeEquipe.objects.create(groupe=groupe, equipe=e1)
    GroupeEquipe.objects.create(groupe=groupe, equipe=e2)

    match = Match.objects.create(
        edition=edition,
        phase_globale=phase,
        sous_phase=sp,
        groupe=groupe,
        equipe_a=e1,
        equipe_b=e2,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.post(f"/api/admin/matchs/{match.id}/score/valider/", {}, format="json")
    assert resp.status_code == 400
