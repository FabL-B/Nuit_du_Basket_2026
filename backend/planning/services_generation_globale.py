from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from core.models import Edition
from matchs.models import Match, StatutMatch
from phases.models import TypePhaseGlobale
from planning.models import Creneau, Terrain


class ErreurGenerationPlanningEdition(ValueError):
    pass


@dataclass(frozen=True)
class ResumeGenerationPlanningEdition:
    matchs_planifies: int
    creneaux_utilises: int
    terrains_utilises: int


def _datetime_debut_edition(edition: Edition) -> datetime:
    start_dt = datetime.combine(edition.date_evenement, edition.heure_debut)
    return timezone.make_aware(start_dt)


def _get_or_create_creneaux_pour_edition(edition: Edition, nb_minimum: int) -> list[Creneau]:
    """
    Garantit qu'il existe au moins nb_minimum créneaux pour l'édition.
    """
    existants = list(
        Creneau.objects.filter(edition=edition).order_by("index")
    )
    if len(existants) >= nb_minimum:
        return existants

    start_dt = _datetime_debut_edition(edition)
    slot_minutes = edition.duree_creneau_minutes

    next_index = existants[-1].index + 1 if existants else 1
    next_start = (
        existants[-1].debut + timedelta(minutes=existants[-1].duree_minutes)
        if existants
        else start_dt
    )

    a_creer = []
    while len(existants) + len(a_creer) < nb_minimum:
        a_creer.append(
            Creneau(
                edition=edition,
                index=next_index,
                debut=next_start,
                duree_minutes=slot_minutes,
            )
        )
        next_index += 1
        next_start = next_start + timedelta(minutes=slot_minutes)

    Creneau.objects.bulk_create(a_creer)

    return list(
        Creneau.objects.filter(edition=edition).order_by("index")
    )


def _ordre_phase(type_phase: str) -> int:
    if type_phase == TypePhaseGlobale.PHASE_1:
        return 1
    if type_phase == TypePhaseGlobale.PHASE_2:
        return 2
    if type_phase == TypePhaseGlobale.FINALE:
        return 3
    return 99


@transaction.atomic
def generer_planning_edition(edition: Edition) -> ResumeGenerationPlanningEdition:
    """
    Génère le planning global de l'édition pour tous les matchs A_PLANIFIER.

    V1 volontairement simple :
    - ordre global stable
    - remplissage séquentiel des terrains puis créneaux
    - compatible avec matchs réels ou théoriques
    """
    if Match.objects.filter(edition=edition, creneau__isnull=False).exists():
        raise ErreurGenerationPlanningEdition(
            "Des matchs sont déjà planifiés pour cette édition. "
            "Suppression manuelle requise avant régénération."
        )

    terrains = list(
        Terrain.objects.filter(edition=edition, est_actif=True).order_by("ordre", "id")
    )
    if not terrains:
        raise ErreurGenerationPlanningEdition(
            "Aucun terrain actif pour cette édition."
        )

    matchs = list(
        Match.objects.filter(
            edition=edition,
            statut=StatutMatch.A_PLANIFIER,
        )
        .select_related(
            "phase_globale",
            "sous_phase",
            "groupe",
            "creneau",
            "terrain",
        )
        .order_by(
            "phase_globale__type_phase",
            "sous_phase_id",
            "groupe_id",
            "id",
        )
    )

    if not matchs:
        return ResumeGenerationPlanningEdition(
            matchs_planifies=0,
            creneaux_utilises=0,
            terrains_utilises=len(terrains),
        )

    # tri Python pour garantir PHASE_1 -> PHASE_2 -> FINALE
    matchs.sort(
        key=lambda m: (
            _ordre_phase(m.phase_globale.type_phase),
            m.sous_phase_id or 0,
            m.groupe_id or 0,
            m.id,
        )
    )

    nb_terrains = len(terrains)
    nb_min_creneaux = (len(matchs) + nb_terrains - 1) // nb_terrains
    creneaux = _get_or_create_creneaux_pour_edition(edition, nb_min_creneaux)

    for index_match, match in enumerate(matchs):
        slot_index = index_match // nb_terrains
        terrain_index = index_match % nb_terrains

        # sécurité si la liste grandit
        if slot_index >= len(creneaux):
            creneaux = _get_or_create_creneaux_pour_edition(edition, slot_index + 1)

        match.creneau = creneaux[slot_index]
        match.terrain = terrains[terrain_index]
        match.statut = StatutMatch.PLANIFIE

    Match.objects.bulk_update(matchs, ["creneau", "terrain", "statut", "modifie_le"])

    creneaux_utilises = ((len(matchs) - 1) // nb_terrains) + 1

    return ResumeGenerationPlanningEdition(
        matchs_planifies=len(matchs),
        creneaux_utilises=creneaux_utilises,
        terrains_utilises=len(terrains),
    )