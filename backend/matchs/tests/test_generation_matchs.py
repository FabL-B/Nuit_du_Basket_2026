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


@pytest.mark.django_db
def test_phase2_genere_matchs_round_robin_par_groupe():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    # Phase 2
    phase2 = PhaseGlobale.objects.create(
        edition=edition,
        type_phase=TypePhaseGlobale.PHASE_2,
        sequence=1,
    )

    sp_ch = SousPhase.objects.create(
        phase_globale=phase2,
        tournoi=tournoi,
        branche=BrancheSousPhase.CHALLENGE,
    )
    sp_co = SousPhase.objects.create(
        phase_globale=phase2,
        tournoi=tournoi,
        branche=BrancheSousPhase.CONSOLANTE,
    )

    # Challenge: 3 équipes => 3 matchs
    g_ch = Groupe.objects.create(sous_phase=sp_ch, code="A")
    e1 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE
    )
    e2 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE
    )
    e3 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E3", statut=StatutEquipe.VALIDEE
    )
    for e in (e1, e2, e3):
        GroupeEquipe.objects.create(groupe=g_ch, equipe=e)

    # Consolante: 4 équipes => 6 matchs
    g_co = Groupe.objects.create(sous_phase=sp_co, code="B")
    e4 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E4", statut=StatutEquipe.VALIDEE
    )
    e5 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E5", statut=StatutEquipe.VALIDEE
    )
    e6 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E6", statut=StatutEquipe.VALIDEE
    )
    e7 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E7", statut=StatutEquipe.VALIDEE
    )
    for e in (e4, e5, e6, e7):
        GroupeEquipe.objects.create(groupe=g_co, equipe=e)

    # Act
    resume = generer_matchs_pour_phase_globale(phase2)

    # Assert
    # 3 (round-robin à 3) + 6 (round-robin à 4) = 9 matchs
    assert resume.matchs_crees == 9

    assert Match.objects.filter(phase_globale=phase2).count() == 9
    assert Match.objects.filter(phase_globale=phase2, statut=StatutMatch.A_PLANIFIER).count() == 9

    # Vérifie que tout est bien rattaché à la bonne sous-phase/groupe
    assert Match.objects.filter(groupe=g_ch, sous_phase=sp_ch).count() == 3
    assert Match.objects.filter(groupe=g_co, sous_phase=sp_co).count() == 6


@pytest.mark.django_db
def test_phase2_refuse_si_matchs_deja_generes():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase2 = PhaseGlobale.objects.create(
        edition=edition,
        type_phase=TypePhaseGlobale.PHASE_2,
        sequence=1,
    )
    sp = SousPhase.objects.create(
        phase_globale=phase2,
        tournoi=tournoi,
        branche=BrancheSousPhase.CHALLENGE,
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

    # On simule qu'un match existe déjà
    Match.objects.create(
        edition=edition,
        phase_globale=phase2,
        sous_phase=sp,
        groupe=g,
        equipe_a=e1,
        equipe_b=e2,
        statut=StatutMatch.A_PLANIFIER,
    )

    with pytest.raises(Exception):
        generer_matchs_pour_phase_globale(phase2)
