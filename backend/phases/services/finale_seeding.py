from __future__ import annotations

from typing import List, Optional, Tuple


class ErreurSeeding(ValueError):
    pass


def generer_paires_premier_tour(equipes_triees: List[str]) -> List[Tuple[Optional[str], Optional[str]]]:
    """
    Prend une liste d'équipes déjà triées par seed (index 0 = seed 1).
    Retourne les paires du premier tour, avec BYE représenté par None.

    Règles:
    - min 4 équipes, max 16
    - 4 -> demis (2 matchs)
    - 5..8 -> quarts (4 matchs, BYE si <8)
    - 9..16 -> huitièmes (8 matchs, BYE si <16)
    """
    n = len(equipes_triees)
    if n < 4:
        raise ErreurSeeding("Phase finale: minimum 4 équipes requises.")
    if n > 16:
        raise ErreurSeeding("Phase finale: maximum 16 équipes.")

    nb_slots = 4 if n <= 4 else 8 if n <= 8 else 16
    # bracket positions standard (1-indexed seeds):
    # on utilise une "liste de positions" qui donne l'ordre des seeds à placer dans les slots
    positions = _positions_standard(nb_slots)

    # on place les seeds existantes, et les seeds manquantes deviennent des BYE
    # seed i correspond à equipes_triees[i-1]
    slots: List[Optional[str]] = [None] * nb_slots
    for slot_index, seed in enumerate(positions):
        if seed <= n:
            slots[slot_index] = equipes_triees[seed - 1]
        else:
            slots[slot_index] = None

    # paires: (slot1 vs slot2), (slot3 vs slot4)...
    paires: List[Tuple[Optional[str], Optional[str]]] = []
    for i in range(0, nb_slots, 2):
        paires.append((slots[i], slots[i + 1]))
    return paires


def _positions_standard(nb_slots: int) -> List[int]:
    """
    Génère l'ordre de placement standard des seeds dans un bracket.
    Exemples:
    4 slots  -> [1,4,2,3]  => 1v4 et 2v3
    8 slots  -> [1,8,4,5,3,6,2,7]
    16 slots -> [1,16,8,9,5,12,4,13,3,14,6,11,7,10,2,15]
    """
    if nb_slots not in (4, 8, 16):
        raise ErreurSeeding(f"nb_slots invalide: {nb_slots}")

    positions = [1, nb_slots]
    step = nb_slots // 2
    while step >= 2:
        new_positions: List[int] = []
        for p in positions:
            new_positions.append(p)
            new_positions.append(step * 2 + 1 - p)
        positions = new_positions
        step //= 2

    # le schéma ci-dessus ne marche pas tel quel pour 4, on force les listes standard
    if nb_slots == 4:
        return [1, 4, 2, 3]
    if nb_slots == 8:
        return [1, 8, 4, 5, 3, 6, 2, 7]
    return [1, 16, 8, 9, 5, 12, 4, 13, 3, 14, 6, 11, 7, 10, 2, 15]
