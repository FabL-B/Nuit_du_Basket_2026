# planning/tests/test_planning_global.py

import pytest
from datetime import date, datetime, time, timedelta
from types import SimpleNamespace

from django.utils import timezone

from core.models import Edition
from phases.models import PhaseGlobale, TypePhaseGlobale
from planning.models import Creneau, PausePlanning
from planning.services_global import (
    ErreurPlanningGlobal,
    generer_planning_global,
)


def _mk_edition():
    return Edition.objects.create(
        nom="NDB 2026",
        date_evenement=date(2026, 6, 20),
        # heure_debut + duree_creneau_minutes déjà par défaut dans ton modèle, mais on les fixe pour le test
        heure_debut=time(14, 0),
        duree_creneau_minutes=15,
    )


def _mk_phase(edition, type_phase: str):
    return PhaseGlobale.objects.create(
        edition=edition,
        type_phase=type_phase,
        sequence=1,
    )


def _mk_creneaux(edition, n=10):
    """
    On crée des créneaux avec des débuts séquentiels (14:00, 14:15, ...).
    Le service services_pauses.py recalculera ensuite ces 'debut' en sautant les pauses.
    """
    start = timezone.make_aware(datetime.combine(edition.date_evenement, edition.heure_debut))
    slot = edition.duree_creneau_minutes

    for i in range(1, n + 1):
        Creneau.objects.create(
            edition=edition,
            index=i,
            debut=start + timedelta(minutes=(i - 1) * slot),
        )


@pytest.mark.django_db
def test_planning_global_sans_pause_ne_deplace_pas_les_creneaux(monkeypatch):
    edition = _mk_edition()
    phase1 = _mk_phase(edition, TypePhaseGlobale.PHASE_1)
    _mk_creneaux(edition, n=8)

    # Stub du planning par phase (on ne teste pas services_planning ici)
    def _fake_generer_planning_phase_globale(_phase):
        return SimpleNamespace(matchs_planifies=42, creneaux_utilises=3)

    monkeypatch.setattr(
        "planning.services_planning.generer_planning_phase_globale",
        _fake_generer_planning_phase_globale,
    )

    before = dict(Creneau.objects.filter(edition=edition).values_list("id", "debut"))

    resume = generer_planning_global(
        edition,
        phase1,
        phase2=None,
        phase_finale=None,
        heure_debut_concours=None,
        duree_concours_minutes=None,
    )

    after = dict(Creneau.objects.filter(edition=edition).values_list("id", "debut"))

    assert resume.phase1_matchs_planifies == 42
    assert resume.phase2_matchs_planifies == 0
    assert resume.finale_matchs_planifies == 0
    assert resume.pause_creee is False
    assert resume.creneaux_deplaces == 0
    assert before == after


@pytest.mark.django_db
def test_planning_global_avec_concours_cree_pause_et_decale_les_creneaux(monkeypatch):
    edition = _mk_edition()
    phase1 = _mk_phase(edition, TypePhaseGlobale.PHASE_1)

    # 8 créneaux => 14:00 .. 15:45 (slot=15min)
    _mk_creneaux(edition, n=8)

    def _fake_generer_planning_phase_globale(_phase):
        return SimpleNamespace(matchs_planifies=10, creneaux_utilises=2)

    monkeypatch.setattr(
        "planning.services_planning.generer_planning_phase_globale",
        _fake_generer_planning_phase_globale,
    )

    # Pause à 15:00 pendant 60 min => tout créneau dont le début tombe dans [15:00, 16:00) doit sauter à 16:00
    resume = generer_planning_global(
        edition,
        phase1,
        phase2=None,
        phase_finale=None,
        heure_debut_concours=time(15, 0),
        duree_concours_minutes=60,
    )

    assert resume.pause_creee is True
    assert PausePlanning.objects.filter(edition=edition, est_active=True).count() == 1
    assert resume.creneaux_deplaces > 0

    # Vérif concrète : le créneau index=5 était 15:00, il doit devenir 16:00
    c5 = Creneau.objects.get(edition=edition, index=5)
    assert c5.debut == timezone.make_aware(datetime.combine(edition.date_evenement, time(16, 0)))


@pytest.mark.django_db
def test_planning_global_refuse_parametres_concours_incomplets(monkeypatch):
    edition = _mk_edition()
    phase1 = _mk_phase(edition, TypePhaseGlobale.PHASE_1)
    _mk_creneaux(edition, n=3)

    def _fake_generer_planning_phase_globale(_phase):
        return SimpleNamespace(matchs_planifies=1, creneaux_utilises=1)

    monkeypatch.setattr(
        "planning.services_planning.generer_planning_phase_globale",
        _fake_generer_planning_phase_globale,
    )

    with pytest.raises(ErreurPlanningGlobal):
        generer_planning_global(
            edition,
            phase1,
            phase2=None,
            phase_finale=None,
            heure_debut_concours=time(15, 0),
            duree_concours_minutes=None,
        )

    with pytest.raises(ErreurPlanningGlobal):
        generer_planning_global(
            edition,
            phase1,
            phase2=None,
            phase_finale=None,
            heure_debut_concours=None,
            duree_concours_minutes=60,
        )
