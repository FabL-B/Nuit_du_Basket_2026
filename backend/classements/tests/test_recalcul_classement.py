from datetime import date

import pytest
from django.contrib.auth import get_user_model

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe, GroupeEquipe
from matchs.models import Match
from matchs.services_scores import saisir_score, valider_score
from classements.models import Classement


@pytest.mark.django_db
def test_recalcul_automatique_classement_a_validation_score():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sp = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sp, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)
    e3 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E3", statut=StatutEquipe.VALIDEE)
    e4 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E4", statut=StatutEquipe.VALIDEE)

    for e in (e1, e2, e3, e4):
        GroupeEquipe.objects.create(groupe=groupe, equipe=e)

    # Match : E1 vs E2 => 10-8 (E1 gagne)
    m = Match.objects.create(
        edition=edition, phase_globale=phase, sous_phase=sp, groupe=groupe, equipe_a=e1, equipe_b=e2
    )

    saisir_score(m, 10, 8)
    User = get_user_model()
    admin = User.objects.create(username="admin")
    valider_score(m, admin)

    c1 = Classement.objects.get(groupe=groupe, equipe=e1)
    c2 = Classement.objects.get(groupe=groupe, equipe=e2)
    c3 = Classement.objects.get(groupe=groupe, equipe=e3)
    c4 = Classement.objects.get(groupe=groupe, equipe=e4)

    assert c1.joues == 1 and c1.gagnes == 1 and c1.points_classement == 3
    assert c2.joues == 1 and c2.perdus == 1 and c2.points_classement == 1

    # équipes non concernées => ligne présente mais à 0
    assert c3.joues == 0 and c3.points_classement == 0
    assert c4.joues == 0 and c4.points_classement == 0
