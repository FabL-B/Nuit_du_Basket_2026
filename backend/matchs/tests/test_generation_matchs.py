from datetime import date

import pytest

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe, GroupeEquipe
from matchs.models import Match, StatutMatch
from matchs.services_generation import generer_matchs_pour_phase_globale, ErreurGenerationMatchs


@pytest.mark.django_db
def test_generation_matchs_sur_tous_les_groupes_de_phase_globale():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))

    # 3 tournois
    t_rookie = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    t_loisir = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    t_compet = Tournoi.objects.create(edition=edition, code=CodeTournoi.COMPETITEUR)

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )

    # sous-phases
    sp_r = SousPhase.objects.create(
        phase_globale=phase, tournoi=t_rookie, branche=BrancheSousPhase.AUCUNE
    )
    sp_l = SousPhase.objects.create(
        phase_globale=phase, tournoi=t_loisir, branche=BrancheSousPhase.AUCUNE
    )
    sp_c = SousPhase.objects.create(
        phase_globale=phase, tournoi=t_compet, branche=BrancheSousPhase.AUCUNE
    )

    # 1 groupe par sous-phase, 4 équipes -> 6 matchs par groupe
    def build_group(sp, prefix):
        g = Groupe.objects.create(sous_phase=sp, code="A")
        equipes = []
        for i in range(4):
            e = Equipe.objects.create(
                edition=edition, tournoi=sp.tournoi, nom=f"{prefix}{i}", statut=StatutEquipe.VALIDEE
            )
            equipes.append(e)
            GroupeEquipe.objects.create(groupe=g, equipe=e)
        return g

    build_group(sp_r, "R")
    build_group(sp_l, "L")
    build_group(sp_c, "C")

    resume = generer_matchs_pour_phase_globale(phase)

    assert resume.groupes_traites == 3
    assert resume.matchs_crees == 18  # 3 groupes * (4*3/2)

    assert Match.objects.filter(phase_globale=phase).count() == 18
    assert (
        Match.objects.filter(
            statut=StatutMatch.A_PLANIFIER, creneau__isnull=True, terrain__isnull=True
        ).count()
        == 18
    )


@pytest.mark.django_db
def test_refuse_regeneration_si_matchs_existent():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sp = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )
    g = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE
    )
    e2 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE
    )
    GroupeEquipe.objects.create(groupe=g, equipe=e1)
    GroupeEquipe.objects.create(groupe=g, equipe=e2)

    generer_matchs_pour_phase_globale(phase)

    with pytest.raises(ErreurGenerationMatchs):
        generer_matchs_pour_phase_globale(phase)
