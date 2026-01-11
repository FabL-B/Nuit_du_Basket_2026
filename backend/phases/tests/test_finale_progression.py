import pytest
from datetime import date

from core.models import Edition
from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match, StatutMatch, Score, TourFinale
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from tournois.models import Tournoi, CodeTournoi

from phases.services.finale_progression import (
    avancer_bracket_si_possible,
    ErreurProgressionFinale,
)


def _setup_base():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase_finale = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.FINALE, sequence=1
    )
    sp_finale = SousPhase.objects.create(
        phase_globale=phase_finale, tournoi=tournoi, branche=BrancheSousPhase.CHALLENGE
    )

    # 4 équipes pour faire 2 demis => une finale potentielle
    equipes = [
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"E{i+1}", statut=StatutEquipe.VALIDEE
        )
        for i in range(4)
    ]
    return edition, tournoi, phase_finale, sp_finale, equipes


@pytest.mark.django_db
def test_progression_ignore_si_pas_phase_finale():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase1 = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sp = SousPhase.objects.create(
        phase_globale=phase1, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)

    m = Match.objects.create(
        edition=edition, phase_globale=phase1, sous_phase=sp, groupe=None,
        equipe_a=e1, equipe_b=e2, statut=StatutMatch.TERMINE,
        tour_finale=TourFinale.DEMI, numero_tour=1,
    )

    assert avancer_bracket_si_possible(m) is None


@pytest.mark.django_db
def test_progression_raise_si_tour_ou_numero_absent():
    _, _, phase_finale, sp_finale, equipes = _setup_base()

    m = Match.objects.create(
        edition=phase_finale.edition, phase_globale=phase_finale, sous_phase=sp_finale, groupe=None,
        equipe_a=equipes[0], equipe_b=equipes[1], statut=StatutMatch.TERMINE,
        tour_finale=None, numero_tour=None,
    )

    with pytest.raises(ErreurProgressionFinale):
        avancer_bracket_si_possible(m)


@pytest.mark.django_db
def test_progression_ne_fait_rien_si_match_pas_finalise():
    _, _, phase_finale, sp_finale, equipes = _setup_base()

    demi1 = Match.objects.create(
        edition=phase_finale.edition, phase_globale=phase_finale, sous_phase=sp_finale, groupe=None,
        equipe_a=equipes[0], equipe_b=equipes[1], statut=StatutMatch.PLANIFIE,
        tour_finale=TourFinale.DEMI, numero_tour=1,
    )

    assert avancer_bracket_si_possible(demi1) is None
    assert not Match.objects.filter(
        phase_globale=phase_finale, sous_phase=sp_finale, tour_finale=TourFinale.FINALE
    ).exists()


@pytest.mark.django_db
def test_progression_ne_fait_rien_si_frere_pas_finalise():
    _, _, phase_finale, sp_finale, equipes = _setup_base()

    demi1 = Match.objects.create(
        edition=phase_finale.edition, phase_globale=phase_finale, sous_phase=sp_finale, groupe=None,
        equipe_a=equipes[0], equipe_b=equipes[3], statut=StatutMatch.TERMINE,
        tour_finale=TourFinale.DEMI, numero_tour=1,
    )
    Score.objects.create(match=demi1, points_a=10, points_b=5, valide_le=None, valide_par=None)

    demi2 = Match.objects.create(
        edition=phase_finale.edition, phase_globale=phase_finale, sous_phase=sp_finale, groupe=None,
        equipe_a=equipes[1], equipe_b=equipes[2], statut=StatutMatch.PLANIFIE,
        tour_finale=TourFinale.DEMI, numero_tour=2,
    )

    assert avancer_bracket_si_possible(demi1) is None
    assert avancer_bracket_si_possible(demi2) is None
    assert Match.objects.filter(
        phase_globale=phase_finale, sous_phase=sp_finale, tour_finale=TourFinale.FINALE
    ).count() == 0


@pytest.mark.django_db
def test_progression_cree_finale_quand_les_deux_demis_sont_finalises():
    _, _, phase_finale, sp_finale, equipes = _setup_base()

    # demi 1 : E1 bat E4
    demi1 = Match.objects.create(
        edition=phase_finale.edition, phase_globale=phase_finale, sous_phase=sp_finale, groupe=None,
        equipe_a=equipes[0], equipe_b=equipes[3], statut=StatutMatch.TERMINE,
        tour_finale=TourFinale.DEMI, numero_tour=1,
    )
    s1 = Score.objects.create(match=demi1, points_a=10, points_b=5, valide_le=None, valide_par=None)
    # on simule un score "validé" (ton service scores le fait normalement)
    Score.objects.filter(pk=s1.pk).update(valide_le="2026-06-20T14:00:00Z")

    # demi 2 : E2 bat E3
    demi2 = Match.objects.create(
        edition=phase_finale.edition, phase_globale=phase_finale, sous_phase=sp_finale, groupe=None,
        equipe_a=equipes[1], equipe_b=equipes[2], statut=StatutMatch.TERMINE,
        tour_finale=TourFinale.DEMI, numero_tour=2,
    )
    s2 = Score.objects.create(match=demi2, points_a=7, points_b=3, valide_le=None, valide_par=None)
    Score.objects.filter(pk=s2.pk).update(valide_le="2026-06-20T14:00:00Z")

    created = avancer_bracket_si_possible(demi1)
    if created is None:
        created = avancer_bracket_si_possible(demi2)

    assert created is not None
    assert created.tour_finale == TourFinale.FINALE
    assert created.numero_tour == 1

    # ordre stable: vainqueur du match numero 1 en equipe_a
    assert created.equipe_a_id == equipes[0].id  # E1
    assert created.equipe_b_id == equipes[1].id  # E2


@pytest.mark.django_db
def test_progression_idempotente_si_finale_deja_creee():
    _, _, phase_finale, sp_finale, equipes = _setup_base()

    demi1 = Match.objects.create(
        edition=phase_finale.edition, phase_globale=phase_finale, sous_phase=sp_finale, groupe=None,
        equipe_a=equipes[0], equipe_b=equipes[3], statut=StatutMatch.FORFAIT_B,
        tour_finale=TourFinale.DEMI, numero_tour=1,
    )
    demi2 = Match.objects.create(
        edition=phase_finale.edition, phase_globale=phase_finale, sous_phase=sp_finale, groupe=None,
        equipe_a=equipes[1], equipe_b=equipes[2], statut=StatutMatch.FORFAIT_B,
        tour_finale=TourFinale.DEMI, numero_tour=2,
    )

    created1 = avancer_bracket_si_possible(demi1)
    if created1 is None:
        created1 = avancer_bracket_si_possible(demi2)

    assert created1 is not None
    assert Match.objects.filter(
        phase_globale=phase_finale, sous_phase=sp_finale, tour_finale=TourFinale.FINALE
    ).count() == 1

    # second appel: ne doit rien recréer
    assert avancer_bracket_si_possible(demi1) is None
    assert avancer_bracket_si_possible(demi2) is None
    assert Match.objects.filter(
        phase_globale=phase_finale, sous_phase=sp_finale, tour_finale=TourFinale.FINALE
    ).count() == 1
