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
    return User.objects.create_superuser(username="admin", email="admin@test.com", password="admin123")


def setup_phase1_minimale():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    # tournois nécessaires au preview (à adapter si ton service exige les 3)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.COMPETITEUR)

    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)
    return phase1

def setup_phase1_avec_tournois_et_equipes():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")

    tournoi_rookie = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    # si ton système exige les 3 tournois, garde-les
    Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.COMPETITEUR)

    phase1 = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1)

    # Pré-requis groupes: minimum 8 équipes (tu l’as confirmé)
    for i in range(8):
        Equipe.objects.create(
            edition=edition,
            tournoi=tournoi_rookie,
            nom=f"E{i+1}",
            statut=StatutEquipe.VALIDEE,
        )

    return phase1

def test_phase2_preview_ok():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    phase1 = setup_phase1_avec_tournois_et_equipes()

    # 1) Générer les sous-phases
    r_sp = client.post(f"/api/admin/phases-globales/{phase1.id}/generer-sous-phases/", data={}, format="json")
    assert r_sp.status_code == 200, r_sp.data

    # 2) Récupérer une sous-phase Rookie (DB) pour générer les groupes
    sous_phase_id = SousPhase.objects.get(
        phase_globale=phase1,
        tournoi__code=CodeTournoi.ROOKIE,
    ).id

    # 3) Générer les groupes phase 1
    r_g = client.post(f"/api/admin/sous-phases/{sous_phase_id}/generer-groupes-phase1/", data={}, format="json")
    assert r_g.status_code == 200, r_g.data

    # 4) Générer les matchs de la phase 1 (round-robin)
    r_m = client.post(f"/api/admin/phases-globales/{phase1.id}/generer-matchs/", data={}, format="json")
    assert r_m.status_code == 200, r_m.data

    # 4bis) Finaliser tous les matchs (score + validation)
    match_ids = list(Match.objects.filter(phase_globale=phase1).values_list("id", flat=True))
    assert match_ids, "Aucun match généré."

    for match_id in match_ids:
        r_score = client.post(
            f"/api/admin/matchs/{match_id}/score/",
            data={"points_a": 10, "points_b": 8},
            format="json",
        )
        assert r_score.status_code == 200, r_score.data

        r_val = client.post(
            f"/api/admin/matchs/{match_id}/score/valider/",
            data={},
            format="json",
        )
        assert r_val.status_code == 200, r_val.data

    # 5) Clôturer la phase 1
    r_close = client.post(f"/api/admin/phases-globales/{phase1.id}/cloturer/", data={}, format="json")
    assert r_close.status_code == 200, r_close.data

    # 6) Preview phase 2
    r_preview = client.get(f"/api/admin/phases-globales/{phase1.id}/phase2-preview/")
    assert r_preview.status_code == 200, r_preview.data
    assert "phase2_id" in r_preview.data
    assert isinstance(r_preview.data.get("propositions"), list)

def test_phase2_preview_refuse_si_phase1_non_cloturee():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    phase1 = setup_phase1_minimale()

    url = f"/api/admin/phases-globales/{phase1.id}/phase2-preview/"
    r = client.get(url)

    assert r.status_code == 400, r.data
    assert "clôtur" in r.data["detail"].lower()

def test_phase2_preview_refuse_si_pas_phase1():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    phase_finale = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.FINALE)

    url = f"/api/admin/phases-globales/{phase_finale.id}/phase2-preview/"
    r = client.get(url)

    assert r.status_code == 400, r.data
    assert "detail" in r.data
