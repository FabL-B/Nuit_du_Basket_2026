import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from core.models import Edition
from phases.models import PhaseGlobale, TypePhaseGlobale, SousPhase
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match

pytestmark = pytest.mark.django_db


def mk_admin():
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )


def setup_phase1_rookie_equipes(nb_equipes: int):
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)

    for i in range(nb_equipes):
        Equipe.objects.create(
            edition=edition,
            tournoi=tournoi,
            nom=f"E{i+1}",
            statut=StatutEquipe.VALIDEE,
        )

    return edition, phase1


def finaliser_matchs(client, phase1):
    match_ids = list(Match.objects.filter(phase_globale=phase1).values_list("id", flat=True))
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


def rendre_phase1_cloturable(client, phase1):
    # sous-phases
    r_sp = client.post(
        f"/api/admin/phases-globales/{phase1.id}/generer-sous-phases/", data={}, format="json"
    )
    assert r_sp.status_code == 200, r_sp.data

    # groupes rookie
    sp_id = SousPhase.objects.get(phase_globale=phase1, tournoi__code=CodeTournoi.ROOKIE).id
    r_g = client.post(
        f"/api/admin/sous-phases/{sp_id}/generer-groupes-phase1/", data={}, format="json"
    )
    assert r_g.status_code == 200, r_g.data

    # matchs
    r_m = client.post(
        f"/api/admin/phases-globales/{phase1.id}/generer-matchs/", data={}, format="json"
    )
    assert r_m.status_code == 200, r_m.data

    # finaliser
    finaliser_matchs(client, phase1)

    # cloturer
    r_close = client.post(
        f"/api/admin/phases-globales/{phase1.id}/cloturer/", data={}, format="json"
    )
    assert r_close.status_code == 200, r_close.data


def test_phase2_generer_refuse_si_decision_impair_absente():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    # 9 -> impair
    _, phase1 = setup_phase1_rookie_equipes(9)
    rendre_phase1_cloturable(client, phase1)

    # Appel sans decision_impair
    r = client.post(
        f"/api/admin/phases-globales/{phase1.id}/phase2-generer/", data={}, format="json"
    )
    assert r.status_code == 400, r.data
    assert "décision" in r.data["detail"].lower()


def test_phase2_generer_refuse_decision_invalide():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    _, phase1 = setup_phase1_rookie_equipes(9)
    rendre_phase1_cloturable(client, phase1)

    payload = {"decision_impair": {"ROOKIE": "INVALID"}}
    r = client.post(
        f"/api/admin/phases-globales/{phase1.id}/phase2-generer/",
        data=payload,
        format="json",
    )
    assert r.status_code == 400, r.data

    # Peut venir du serializer ou du service, donc on cherche le message où qu'il soit.
    msg = ""
    if isinstance(r.data, dict):
        if "detail" in r.data:
            msg = str(r.data["detail"])
        else:
            msg = str(r.data)

    assert (
        ("invalid" in msg.lower())
        or ("inval" in msg.lower())
        or ("attendu" in msg.lower())
        or ("choice" in msg.lower())
    )


def test_phase2_generer_ok_avec_decision_impair_valide():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    _, phase1 = setup_phase1_rookie_equipes(9)
    rendre_phase1_cloturable(client, phase1)

    payload = {"decision_impair": {CodeTournoi.ROOKIE: "CHALLENGE"}}
    r = client.post(
        f"/api/admin/phases-globales/{phase1.id}/phase2-generer/", data=payload, format="json"
    )
    assert r.status_code == 200, r.data
    assert r.data["created"] is True
    assert r.data["phase2_id"] is not None
