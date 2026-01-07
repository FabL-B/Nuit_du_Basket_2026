from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe
from matchs.models import Match, StatutMatch, Score
from matchs.services_scores import saisir_score, valider_score, ErreurScore


@pytest.mark.django_db
def _setup_match():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sous_phase = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sous_phase, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)

    match = Match.objects.create(
        edition=edition,
        phase_globale=phase,
        sous_phase=sous_phase,
        groupe=groupe,
        equipe_a=e1,
        equipe_b=e2,
    )
    return match


@pytest.mark.django_db
def test_saisir_score_cree_ou_update_non_valide():
    match = _setup_match()

    score = saisir_score(match, 10, 8)
    assert score.points_a == 10
    assert score.points_b == 8
    assert score.valide_le is None

    score2 = saisir_score(match, 12, 9)
    assert score2.id == score.id
    score2.refresh_from_db()
    assert score2.points_a == 12
    assert score2.points_b == 9


@pytest.mark.django_db
def test_valider_score_termine_match_et_verrouille():
    match = _setup_match()
    saisir_score(match, 10, 8)

    User = get_user_model()
    admin = User.objects.create(username="admin")

    score = valider_score(match, admin)
    assert score.valide_le is not None
    assert score.valide_par_id == admin.id

    match.refresh_from_db()
    assert match.statut == StatutMatch.TERMINE

    # modification interdite
    with pytest.raises(ErreurScore):
        saisir_score(match, 11, 11)


@pytest.mark.django_db
def test_refuse_valider_si_pas_de_score():
    match = _setup_match()
    User = get_user_model()
    admin = User.objects.create(username="admin")

    with pytest.raises(ErreurScore):
        valider_score(match, admin)


@pytest.mark.django_db
def test_refuse_score_si_forfait():
    match = _setup_match()
    match.statut = StatutMatch.FORFAIT_A
    match.save()

    with pytest.raises(ErreurScore):
        saisir_score(match, 10, 8)
