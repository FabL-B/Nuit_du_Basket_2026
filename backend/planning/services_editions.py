from dataclasses import dataclass

from django.db import transaction
from django.core.exceptions import ValidationError

from matchs.models import Match


class ErreurEditionPlanning(Exception):
    pass


@dataclass(frozen=True)
class ResumeSwapPlanning:
    match_a_id: int
    match_b_id: int


@transaction.atomic
def swap_planning_matchs(match_a: Match, match_b: Match) -> ResumeSwapPlanning:
    if match_a.id == match_b.id:
        raise ErreurEditionPlanning("Impossible d'interchanger le même match.")

    if not match_a.creneau_id or not match_a.terrain_id:
        raise ErreurEditionPlanning("Le match A n'est pas planifié (créneau/terrain manquant).")
    if not match_b.creneau_id or not match_b.terrain_id:
        raise ErreurEditionPlanning("Le match B n'est pas planifié (créneau/terrain manquant).")

    # swap
    match_a_creneau, match_a_terrain = match_a.creneau_id, match_a.terrain_id
    match_b_creneau, match_b_terrain = match_b.creneau_id, match_b.terrain_id

    match_a.creneau_id, match_a.terrain_id = match_b_creneau, match_b_terrain
    match_b.creneau_id, match_b.terrain_id = match_a_creneau, match_a_terrain

    try:
        match_a.full_clean()
        match_b.full_clean()
        match_a.save(update_fields=["creneau", "terrain"])
        match_b.save(update_fields=["creneau", "terrain"])
    except ValidationError as e:
        raise ErreurEditionPlanning(str(e)) from e

    return ResumeSwapPlanning(match_a_id=match_a.id, match_b_id=match_b.id)
