from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class ErreurBracket(ValueError):
    pass


class TourBracket(str, Enum):
    HUITIEME_FINALE = "HUITIEME"
    QUART_FINALE = "QUART"
    DEMI_FINALE = "DEMI"
    FINALE = "FINALE"


@dataclass(frozen=True)
class FormatBracket:
    tour_depart: TourBracket
    nb_slots: int  # 4, 8, 16


@dataclass(frozen=True)
class MatchBracket:
    """
    Match "structurel" (pas un Match DB).
    - id: identifiant interne stable dans la structure
    - tour: HUITIEME/QUART/DEMI/FINALE
    - index: position dans le tour (1..n)
    - depuis_match_ids: pour les tours suivants, liste des matchs du tour précédent dont proviennent les gagnants
    """
    id: str
    tour: TourBracket
    index: int
    depuis_match_ids: List[str]


def proposer_format_bracket(nb_equipes: int) -> FormatBracket:
    """
    Choisit le tour de départ selon nb_equipes qualifiées.
    Contraintes demandées:
    - minimum demi-finales (=> 4 équipes min)
    - maximum huitièmes (=> 16 équipes max)
    - si nb_equipes non puissance de 2, BYE implicites (slots vides)
    """
    if nb_equipes < 4:
        raise ErreurBracket("Phase finale: minimum 4 équipes requises (2 demis + finale).")
    if nb_equipes > 16:
        raise ErreurBracket("Phase finale: maximum 16 équipes (départ en 1/8).")

    if nb_equipes <= 4:
        return FormatBracket(tour_depart=TourBracket.DEMI_FINALE, nb_slots=4)
    if nb_equipes <= 8:
        return FormatBracket(tour_depart=TourBracket.QUART_FINALE, nb_slots=8)
    return FormatBracket(tour_depart=TourBracket.HUITIEME_FINALE, nb_slots=16)


def generer_structure_bracket(nb_equipes: int) -> List[MatchBracket]:
    """
    Génère la structure complète du bracket du tour de départ jusqu'à la finale.
    Ne place pas les équipes, ne gère pas les BYE explicitement (ce sera au moment d'affecter les seeds).
    """
    fmt = proposer_format_bracket(nb_equipes)

    tours = _tours_depuis(fmt.tour_depart)
    structure: List[MatchBracket] = []

    # génère le premier tour
    nb_matchs_tour = fmt.nb_slots // 2
    precedent_ids: List[str] = []

    for i in range(1, nb_matchs_tour + 1):
        mid = _mk_id(tours[0], i)
        m = MatchBracket(id=mid, tour=tours[0], index=i, depuis_match_ids=[])
        structure.append(m)
        precedent_ids.append(mid)

    # tours suivants : chaque match dépend de 2 matchs du tour précédent
    for tour in tours[1:]:
        nb_matchs_tour = len(precedent_ids) // 2
        nouveaux_ids: List[str] = []

        for i in range(1, nb_matchs_tour + 1):
            mid = _mk_id(tour, i)
            deps = [precedent_ids[(i - 1) * 2], precedent_ids[(i - 1) * 2 + 1]]
            m = MatchBracket(id=mid, tour=tour, index=i, depuis_match_ids=deps)
            structure.append(m)
            nouveaux_ids.append(mid)

        precedent_ids = nouveaux_ids

    return structure


def _tours_depuis(tour_depart: TourBracket) -> List[TourBracket]:
    if tour_depart == TourBracket.DEMI_FINALE:
        return [TourBracket.DEMI_FINALE, TourBracket.FINALE]
    if tour_depart == TourBracket.QUART_FINALE:
        return [TourBracket.QUART_FINALE, TourBracket.DEMI_FINALE, TourBracket.FINALE]
    if tour_depart == TourBracket.HUITIEME_FINALE:
        return [
            TourBracket.HUITIEME_FINALE,
            TourBracket.QUART_FINALE,
            TourBracket.DEMI_FINALE,
            TourBracket.FINALE,
        ]
    raise ErreurBracket(f"Tour de départ inconnu: {tour_depart}")


def _mk_id(tour: TourBracket, index: int) -> str:
    return f"{tour.value}-{index}"
