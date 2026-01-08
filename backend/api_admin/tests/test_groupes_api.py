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
def test_non_admin_refuse_groupes_list():
    User = get_user_model()
    user = User.objects.create_user(username="user", password="pass", is_staff=False)

    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/admin/groupes/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_admin_peut_swap_equipes_entre_deux_groupes_meme_sous_phase():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)

    g1 = Groupe.objects.create(sous_phase=sp, code="A")
    g2 = Groupe.objects.create(sous_phase=sp, code="B")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)

    GroupeEquipe.objects.create(groupe=g1, equipe=e1)
    GroupeEquipe.objects.create(groupe=g2, equipe=e2)

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.post(
        "/api/admin/groupes/swap-equipes/",
        {
            "groupe_a_id": g1.id,
            "equipe_a_id": e1.id,
            "groupe_b_id": g2.id,
            "equipe_b_id": e2.id,
        },
        format="json",
    )
    assert resp.status_code == 200

    assert GroupeEquipe.objects.filter(groupe=g1, equipe=e2).exists()
    assert GroupeEquipe.objects.filter(groupe=g2, equipe=e1).exists()
