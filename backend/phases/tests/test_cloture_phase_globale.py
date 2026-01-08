from datetime import date

import pytest
from django.contrib.auth import get_user_model

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe, GroupeEquipe
from matchs.models import Match, StatutMatch
from matchs.services_scores import saisir_score, valider_score
from classements.models import Classement
from phases.services_cloture import cloturer_phase_globale, ErreurCloturePhase


@pytest.mark.django_db
def test_cloture_refuse_si_match_non_finalise():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)
    GroupeEquipe.objects.create(groupe=groupe, equipe=e1)
    GroupeEquipe.objects.create(groupe=groupe, equipe=e2)

    Match.objects.create(
        edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
        equipe_a=e1, equipe_b=e2,
        statut=StatutMatch.PLANIFIE,  # non finalisé
    )

    with pytest.raises(ErreurCloturePhase):
        cloturer_phase_globale(phase)


@pytest.mark.django_db
def test_cloture_refuse_si_egalite_3_plus_sans_rang_manuel():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)
    e3 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E3", statut=StatutEquipe.VALIDEE)

    for e in (e1, e2, e3):
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    admin = get_user_model().objects.create(username="admin")

    # 3 matchs (round-robin) tous nuls => égalité parfaite à 3
    matchs = [
        Match.objects.create(edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
                             equipe_a=e1, equipe_b=e2, statut=StatutMatch.A_PLANIFIER),
        Match.objects.create(edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
                             equipe_a=e1, equipe_b=e3, statut=StatutMatch.A_PLANIFIER),
        Match.objects.create(edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
                             equipe_a=e2, equipe_b=e3, statut=StatutMatch.A_PLANIFIER),
    ]
    for m in matchs:
        saisir_score(m, 10, 10)
        valider_score(m, admin)

    with pytest.raises(ErreurCloturePhase):
        cloturer_phase_globale(phase)


@pytest.mark.django_db
def test_cloture_ok_si_tous_finalises_et_departement_fait():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)
    e3 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E3", statut=StatutEquipe.VALIDEE)

    for e in (e1, e2, e3):
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    admin = get_user_model().objects.create(username="admin")

    matchs = [
        Match.objects.create(edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
                             equipe_a=e1, equipe_b=e2, statut=StatutMatch.A_PLANIFIER),
        Match.objects.create(edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
                             equipe_a=e1, equipe_b=e3, statut=StatutMatch.A_PLANIFIER),
        Match.objects.create(edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
                             equipe_a=e2, equipe_b=e3, statut=StatutMatch.A_PLANIFIER),
    ]
    for m in matchs:
        saisir_score(m, 10, 10)
        valider_score(m, admin)

    # Départage manuel : UPDATE (pas create)
    Classement.objects.filter(groupe=groupe, equipe=e1).update(rang_manuel=1)
    Classement.objects.filter(groupe=groupe, equipe=e2).update(rang_manuel=2)
    Classement.objects.filter(groupe=groupe, equipe=e3).update(rang_manuel=3)

    resume = cloturer_phase_globale(phase)
    assert resume.groupes == 1
    assert resume.matchs_total == 3

