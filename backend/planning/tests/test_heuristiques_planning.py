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
def test_planning_retourne_metriques():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    for i in range(4):
        Terrain.objects.create(edition=edition, nom=f"Int {i+1}", type_terrain=TypeTerrain.INTERIEUR, ordre=i)
    for i in range(4):
        Terrain.objects.create(edition=edition, nom=f"Ext {i+1}", type_terrain=TypeTerrain.EXTERIEUR, ordre=10+i)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    equipes = []
    for i in range(32):
        e = Equipe.objects.create(edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE)
        equipes.append(e)
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    # 16 matchs uniques : (E1 vs E2), (E3 vs E4), ... (E31 vs E32)
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

    assert resume.metriques is not None
    assert resume.metriques.nb_matchs == 16
    assert resume.metriques.nb_equipes > 0
