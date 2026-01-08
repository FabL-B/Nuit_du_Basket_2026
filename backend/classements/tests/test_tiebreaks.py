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
from classements.services import recalculer_classements_pour_groupe
from classements.services_tri import ordonner_classement_groupe


@pytest.mark.django_db
def test_tiebreak_confrontation_directe_2_equipes():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="A", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="B", statut=StatutEquipe.VALIDEE)

    GroupeEquipe.objects.create(groupe=groupe, equipe=e1)
    GroupeEquipe.objects.create(groupe=groupe, equipe=e2)

    # Match direct : e2 bat e1
    m = Match.objects.create(
        edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe,
        equipe_a=e1, equipe_b=e2, statut=StatutMatch.A_PLANIFIER
    )
    saisir_score(m, 10, 12)
    admin = get_user_model().objects.create(username="admin")
    valider_score(m, admin)

    recalculer_classements_pour_groupe(groupe)

    ordre = ordonner_classement_groupe(groupe)
    assert [c.equipe_id for c in ordre] == [e2.id, e1.id]


@pytest.mark.django_db
def test_tiebreak_rang_manuel_departage_dernier_recours():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="A", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="B", statut=StatutEquipe.VALIDEE)

    GroupeEquipe.objects.create(groupe=groupe, equipe=e1)
    GroupeEquipe.objects.create(groupe=groupe, equipe=e2)

    # On crée directement deux classements parfaitement identiques
    Classement.objects.create(groupe=groupe, equipe=e1, points_classement=3, difference=0, points_marques=0, rang_manuel=2)
    Classement.objects.create(groupe=groupe, equipe=e2, points_classement=3, difference=0, points_marques=0, rang_manuel=1)

    ordre = ordonner_classement_groupe(groupe)
    assert [c.equipe_id for c in ordre] == [e2.id, e1.id]
