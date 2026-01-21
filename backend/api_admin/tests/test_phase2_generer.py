import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from core.models import Edition
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match  # adapte si chemin différent

pytestmark = pytest.mark.django_db


def mk_admin():
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )


def setup_phase1_avec_tournois_et_equipes():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi_rookie = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.COMPETITEUR)

    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)

    for i in range(8):
        Equipe.objects.create(
            edition=edition,
            tournoi=tournoi_rookie,
            nom=f"E{i+1}",
            statut=StatutEquipe.VALIDEE,
        )

    return phase1


def finaliser_tous_les_matchs_phase(client, phase):
    match_ids = list(Match.objects.filter(phase_globale=phase).values_list("id", flat=True))
    assert match_ids, "Aucun match généré."

    for match_id in match_ids:
        r_score = client.post(
            f"/api/admin/matchs/{match_id}/score/",
            data={"points_a": 10, "points_b": 8},
            format="json",
        )
        assert r_score.status_code == 200, getattr(r_score, "data", r_score.content)

        r_val = client.post(
            f"/api/admin/matchs/{match_id}/score/valider/",
            data={},
            format="json",
        )
        assert r_val.status_code == 200, getattr(r_val, "data", r_val.content)


def test_phase2_generer_ok():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    phase1 = setup_phase1_avec_tournois_et_equipes()

    # sous-phases
    r_sp = client.post(
        f"/api/admin/phases-globales/{phase1.id}/generer-sous-phases/", data={}, format="json"
    )
    assert r_sp.status_code == 200, r_sp.data

    # groupes (sur sous-phase rookie)
    sous_phase_id = SousPhase.objects.get(phase_globale=phase1, tournoi__code=CodeTournoi.ROOKIE).id
    r_g = client.post(
        f"/api/admin/sous-phases/{sous_phase_id}/generer-groupes-phase1/", data={}, format="json"
    )
    assert r_g.status_code == 200, r_g.data

    # matchs
    r_m = client.post(
        f"/api/admin/phases-globales/{phase1.id}/generer-matchs/", data={}, format="json"
    )
    assert r_m.status_code == 200, r_m.data

    # finaliser + cloturer
    finaliser_tous_les_matchs_phase(client, phase1)

    r_close = client.post(
        f"/api/admin/phases-globales/{phase1.id}/cloturer/", data={}, format="json"
    )
    assert r_close.status_code == 200, r_close.data

    # génération phase 2
    r_gen = client.post(
        f"/api/admin/phases-globales/{phase1.id}/phase2-generer/", data={}, format="json"
    )
    assert r_gen.status_code == 200, r_gen.data
    assert r_gen.data["created"] is True
    assert "phase2_id" in r_gen.data
