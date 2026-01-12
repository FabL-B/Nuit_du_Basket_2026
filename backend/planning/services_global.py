from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Optional

from django.db import transaction
from django.utils import timezone

from core.models import Edition
from phases.models import PhaseGlobale, TypePhaseGlobale
from planning.models import PausePlanning, Creneau
from planning.services_pauses import recalculer_debuts_creneaux_avec_pauses
from planning import services_planning


class ErreurPlanningGlobal(Exception):
    pass


@dataclass(frozen=True)
class ResumePlanningGlobal:
    phase1_matchs_planifies: int
    phase2_matchs_planifies: int
    finale_matchs_planifies: int
    pause_creee: bool
    creneaux_deplaces: int


@transaction.atomic
def generer_planning_global(
    edition: Edition,
    phase1: PhaseGlobale,
    phase2: Optional[PhaseGlobale] = None,
    phase_finale: Optional[PhaseGlobale] = None,
    *,
    heure_debut_concours: Optional[time] = None,
    duree_concours_minutes: Optional[int] = None,
) -> ResumePlanningGlobal:
    """
    Orchestrateur:
    - génère le planning de phase 1 puis 2 puis finale (si présentes)
    - crée une pause concours shoot (optionnelle)
    - recalcule les débuts de créneaux en tenant compte des pauses (idempotent)
    """
    # garde-fous
    if phase1.edition_id != edition.id or phase1.type_phase != TypePhaseGlobale.PHASE_1:
        raise ErreurPlanningGlobal("phase1 invalide (édition ou type).")
    if phase2 and (
        phase2.edition_id != edition.id or phase2.type_phase != TypePhaseGlobale.PHASE_2
    ):
        raise ErreurPlanningGlobal("phase2 invalide (édition ou type).")
    if phase_finale and (
        phase_finale.edition_id != edition.id or phase_finale.type_phase != TypePhaseGlobale.FINALE
    ):
        raise ErreurPlanningGlobal("phase_finale invalide (édition ou type).")

    # 1) planning phase 1
    res1 = services_planning.generer_planning_phase_globale(phase1)

    # 2) planning phase 2
    res2 = services_planning.generer_planning_phase_globale(phase2) if phase2 else None

    # 3) planning finale
    resf = services_planning.generer_planning_phase_globale(phase_finale) if phase_finale else None

    # snapshot des débuts AVANT (pour compter)
    before = dict(Creneau.objects.filter(edition=edition).values_list("id", "debut"))

    # 4) pause concours shoot (optionnelle)
    pause_creee = False
    if heure_debut_concours is not None or duree_concours_minutes is not None:
        if heure_debut_concours is None or duree_concours_minutes is None:
            raise ErreurPlanningGlobal(
                "Concours shoot: heure_debut_concours et duree_concours_minutes requis ensemble."
            )
        if duree_concours_minutes <= 0:
            raise ErreurPlanningGlobal("Concours shoot: durée invalide.")

        if PausePlanning.objects.filter(edition=edition, est_active=True).exists():
            raise ErreurPlanningGlobal("Une pause active existe déjà pour cette édition.")

        debut_dt = timezone.datetime.combine(edition.date_evenement, heure_debut_concours)
        debut_dt = timezone.make_aware(debut_dt, timezone.get_current_timezone())

        PausePlanning.objects.create(
            edition=edition,
            nom="Concours de shoot",
            debut=debut_dt,
            duree_minutes=duree_concours_minutes,
            est_active=True,
        )
        pause_creee = True

    # 5) recalcul des débuts de créneaux avec pauses
    recalculer_debuts_creneaux_avec_pauses(edition)

    # snapshot APRES + comptage
    after = dict(Creneau.objects.filter(edition=edition).values_list("id", "debut"))
    creneaux_deplaces = sum(1 for cid, d0 in before.items() if after.get(cid) != d0)

    return ResumePlanningGlobal(
        phase1_matchs_planifies=res1.matchs_planifies,
        phase2_matchs_planifies=(res2.matchs_planifies if res2 else 0),
        finale_matchs_planifies=(resf.matchs_planifies if resf else 0),
        pause_creee=pause_creee,
        creneaux_deplaces=creneaux_deplaces,
    )
