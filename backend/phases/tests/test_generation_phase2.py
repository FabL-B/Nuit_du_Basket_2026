from datetime import date

import pytest
from django.contrib.auth import get_user_model

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import (
    PhaseGlobale,
    SousPhase,
    TypePhaseGlobale,
    BrancheSousPhase,
    StatutPhase,
)
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe, GroupeEquipe
from matchs.models import Match, StatutMatch
from matchs.services_scores import saisir_score, valider_score
from phases.services_phase2 import (
    generer_phase2_depuis_phase1,
    ErreurGenerationPhase2,
)


def _setup_phase1_cloturee_avec_9_equipes_loisir():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase1 = PhaseGlobale.objects.create(
        edition=edition,
        type_phase=TypePhaseGlobale.PHASE_1,
        sequence=1,
        statut=StatutPhase.BROUILLON,
    )
    sp1 = SousPhase.objects.create(
        phase_globale=phase1,
        tournoi=tournoi,
        branche=BrancheSousPhase.AUCUNE,
        statut=StatutPhase.BROUILLON,
    )

    # Groupe unique A avec 9 équipes
    groupe = Groupe.objects.create(sous_phase=sp1, code="A")
    equipes = []
    for i in range(9):
        e = Equipe.objects.create(
            edition=edition,
            tournoi=tournoi,
            nom=f"E{i+1}",
            statut=StatutEquipe.VALIDEE,
        )
        equipes.append(e)
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    # Pour pouvoir clôturer phase1 : on termine au moins un match (et ici on termine plusieurs)
    admin = get_user_model().objects.create(username="admin")
    # 3 matchs nuls (pas besoin du round robin complet)
    matchs = [
        Match.objects.create(
            edition=edition, phase_globale=phase1, sous_phase=sp1, groupe=groupe,
            equipe_a=equipes[0], equipe_b=equipes[1], statut=StatutMatch.A_PLANIFIER
        ),
        Match.objects.create(
            edition=edition, phase_globale=phase1, sous_phase=sp1, groupe=groupe,
            equipe_a=equipes[2], equipe_b=equipes[3], statut=StatutMatch.A_PLANIFIER
        ),
        Match.objects.create(
            edition=edition, phase_globale=phase1, sous_phase=sp1, groupe=groupe,
            equipe_a=equipes[4], equipe_b=equipes[5], statut=StatutMatch.A_PLANIFIER
        ),
    ]
    for m in matchs:
        saisir_score(m, 10, 10)
        valider_score(m, admin)

    # Clôture phase 1 : ici on doit finaliser tous les matchs de la phase.
    # On n'a créé que 3 matchs => ils sont finalisés => OK.
    phase1.statut = StatutPhase.CLOTUREE
    phase1.save(update_fields=["statut", "modifie_le"])

    return edition, phase1, tournoi


@pytest.mark.django_db
def test_phase2_refuse_si_tournoi_impair_sans_decision_admin():
    edition, phase1, tournoi = _setup_phase1_cloturee_avec_9_equipes_loisir()

    with pytest.raises(ErreurGenerationPhase2):
        generer_phase2_depuis_phase1(phase1, decision_impair={})


@pytest.mark.django_db
def test_phase2_genere_groupes_et_affectations_quand_decision_admin_ok():
    edition, phase1, tournoi = _setup_phase1_cloturee_avec_9_equipes_loisir()

    resume = generer_phase2_depuis_phase1(
        phase1,
        decision_impair={CodeTournoi.LOISIR: "CHALLENGE"},
    )

    assert resume.phase2_id is not None
    assert resume.equipes_challenge + resume.equipes_consolante == 9
    assert resume.equipes_challenge == 5
    assert resume.equipes_consolante == 4

    # Vérifie que les SousPhase Phase 2 existent
    sp_ch = SousPhase.objects.get(
        phase_globale_id=resume.phase2_id,
        tournoi__code=CodeTournoi.LOISIR,
        branche=BrancheSousPhase.CHALLENGE,
    )
    sp_co = SousPhase.objects.get(
        phase_globale_id=resume.phase2_id,
        tournoi__code=CodeTournoi.LOISIR,
        branche=BrancheSousPhase.CONSOLANTE,
    )

    # Vérifie que des groupes ont été créés et que les affectations existent
    assert Groupe.objects.filter(sous_phase=sp_ch).exists()
    assert Groupe.objects.filter(sous_phase=sp_co).exists()

    nb_ch = GroupeEquipe.objects.filter(groupe__sous_phase=sp_ch).count()
    nb_co = GroupeEquipe.objects.filter(groupe__sous_phase=sp_co).count()

    assert nb_ch == 5
    assert nb_co == 4
