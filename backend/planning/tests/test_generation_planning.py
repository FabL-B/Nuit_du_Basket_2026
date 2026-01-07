from datetime import date

import pytest

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe, GroupeEquipe
from matchs.models import Match, StatutMatch
from planning.models import Terrain, TypeTerrain
from planning.services_planning import generer_planning_phase_globale


@pytest.mark.django_db
def test_planning_assigne_creneau_et_terrain_sans_collision():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    # 8 terrains (4 int, 4 ext)
    for i in range(4):
        Terrain.objects.create(
            edition=edition, nom=f"Int {i+1}", type_terrain=TypeTerrain.INTERIEUR, ordre=i
        )
    for i in range(4):
        Terrain.objects.create(
            edition=edition, nom=f"Ext {i+1}", type_terrain=TypeTerrain.EXTERIEUR, ordre=10 + i
        )

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sp = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    # 8 équipes => on crée 8 matchs "artificiels" (pas round robin complet) pour tester collisions
    equipes = []
    for i in range(8):
        e = Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )
        equipes.append(e)
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    # 8 matchs indépendants (E1vsE2, E3vsE4, ...)
    for i in range(0, 8, 2):
        Match.objects.create(
            edition=edition,
            phase_globale=phase,
            sous_phase=sp,
            groupe=groupe,
            equipe_a=equipes[i],
            equipe_b=equipes[i + 1],
            statut=StatutMatch.A_PLANIFIER,
        )

    resume = generer_planning_phase_globale(phase)
    assert resume.matchs_planifies == 4
    assert resume.creneaux_utilises == 1

    matchs = list(Match.objects.filter(phase_globale=phase))
    assert all(m.creneau_id is not None and m.terrain_id is not None for m in matchs)
    assert all(m.statut == StatutMatch.PLANIFIE for m in matchs)

    # Vérif : pas 2 matchs sur le même terrain au même créneau
    seen = set()
    for m in matchs:
        key = (m.creneau_id, m.terrain_id)
        assert key not in seen
        seen.add(key)

    # Vérif : une équipe max par créneau
    teams_by_slot = {}
    for m in matchs:
        teams_by_slot.setdefault(m.creneau_id, set()).update([m.equipe_a_id, m.equipe_b_id])

    for slot_id, team_ids in teams_by_slot.items():
        assert len(team_ids) == len(set(team_ids))


@pytest.mark.django_db
def test_planning_cree_autant_de_creneaux_que_necessaire():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    # 8 terrains
    for i in range(4):
        Terrain.objects.create(
            edition=edition, nom=f"Int {i+1}", type_terrain=TypeTerrain.INTERIEUR, ordre=i
        )
    for i in range(4):
        Terrain.objects.create(
            edition=edition, nom=f"Ext {i+1}", type_terrain=TypeTerrain.EXTERIEUR, ordre=10 + i
        )

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sp = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    # 16 équipes => 8 matchs par "tour" si on les paire, on crée 16 matchs => 2 créneaux attendus
    equipes = []
    for i in range(32):
        e = Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )
        equipes.append(e)

    # On affecte seulement 32 équipes au groupe (pas réaliste mais suffisant pour test planning)
    for e in equipes:
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    # 16 matchs : E1vsE2, E3vsE4, ...
    for i in range(0, 32, 2):
        Match.objects.create(
            edition=edition,
            phase_globale=phase,
            sous_phase=sp,
            groupe=groupe,
            equipe_a=equipes[i],
            equipe_b=equipes[i + 1],
            statut=StatutMatch.A_PLANIFIER,
        )

    resume = generer_planning_phase_globale(phase)
    assert resume.matchs_planifies == 16
    assert resume.creneaux_utilises == 2
