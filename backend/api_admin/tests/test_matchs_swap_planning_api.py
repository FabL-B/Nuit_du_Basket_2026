from datetime import date, datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from groupes.models import Groupe, GroupeEquipe
from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match, StatutMatch
from planning.models import Terrain, Creneau


@pytest.mark.django_db
def test_admin_peut_swap_planning_entre_deux_matchs():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    t1 = Terrain.objects.create(edition=edition, nom="Int 1", type_terrain="INTERIEUR", ordre=1)
    t2 = Terrain.objects.create(edition=edition, nom="Ext 1", type_terrain="EXTERIEUR", ordre=2)

    start = timezone.make_aware(datetime(2026, 6, 20, 14, 0))
    c1 = Creneau.objects.create(edition=edition, index=1, debut=start, duree_minutes=15)
    c2 = Creneau.objects.create(edition=edition, index=2, debut=start + timedelta(minutes=15), duree_minutes=15)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)
    e3 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E3", statut=StatutEquipe.VALIDEE)
    e4 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E4", statut=StatutEquipe.VALIDEE)

    for e in (e1, e2, e3, e4):
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    m1 = Match.objects.create(
        edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
        equipe_a=e1, equipe_b=e2,
        statut=StatutMatch.PLANIFIE,
        creneau=c1, terrain=t1,
    )
    m2 = Match.objects.create(
        edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
        equipe_a=e3, equipe_b=e4,
        statut=StatutMatch.PLANIFIE,
        creneau=c2, terrain=t2,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.post(
        "/api/admin/matchs/swap-planning/",
        {"match_a_id": m1.id, "match_b_id": m2.id},
        format="json",
    )
    assert resp.status_code == 200

    m1.refresh_from_db()
    m2.refresh_from_db()

    assert m1.creneau_id == c2.id and m1.terrain_id == t2.id
    assert m2.creneau_id == c1.id and m2.terrain_id == t1.id
