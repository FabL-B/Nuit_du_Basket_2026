from dataclasses import dataclass

from django.db import transaction

from matchs.models import Match, StatutMatch
from classements.services import recalculer_classements_pour_groupe


class ErreurForfait(Exception):
    pass


@dataclass(frozen=True)
class ResumeForfait:
    match_id: int
    statut_match: str


@transaction.atomic
def declarer_forfait(match: Match, statut_forfait: str) -> ResumeForfait:
    """
    Déclare un forfait sur un match.
    Règles strictes :
    - forfait uniquement sur un match non terminé
    - statut_forfait doit être FORFAIT_A / FORFAIT_B / DOUBLE_FORFAIT
    Effets :
    - match finalisé
    - recalcul classement du groupe
    """
    autorises = {StatutMatch.FORFAIT_A, StatutMatch.FORFAIT_B, StatutMatch.DOUBLE_FORFAIT}
    if statut_forfait not in autorises:
        raise ErreurForfait("Statut forfait invalide.")

    if match.statut == StatutMatch.TERMINE:
        raise ErreurForfait("Forfait impossible : le match est déjà terminé.")

    if match.statut in autorises:
        # idempotent: si déjà forfait, on autorise uniquement si même statut
        if match.statut != statut_forfait:
            raise ErreurForfait("Forfait déjà déclaré avec un autre statut.")
        return ResumeForfait(match_id=match.id, statut_match=match.statut)

    match.statut = statut_forfait
    match.save(update_fields=["statut"])

    # recalcul du groupe (forfaits inclus)
    recalculer_classements_pour_groupe(match.groupe)

    return ResumeForfait(match_id=match.id, statut_match=match.statut)
