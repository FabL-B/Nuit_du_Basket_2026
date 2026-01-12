from __future__ import annotations

from typing import List, Tuple


class ErreurSeeding(ValueError):
    pass


def generer_paires_premier_tour(equipes_triees: List[int]) -> List[Tuple[int, int]]:
    """
    Input:
    - equipes_triees: liste déjà triée par seed (index 0 = seed 1)

    Règle:
    - uniquement 4, 8 ou 16 équipes (pas de BYE)
    """
    n = len(equipes_triees)
    if n not in (4, 8, 16):
        raise ErreurSeeding("Phase finale: format invalide. Attendu exactement 4, 8 ou 16 équipes.")

    positions = _positions_standard(n)

    slots: List[int] = [0] * n
    for slot_index, seed in enumerate(positions):
        slots[slot_index] = equipes_triees[seed - 1]

    return [(slots[i], slots[i + 1]) for i in range(0, n, 2)]


def _positions_standard(nb_slots: int) -> List[int]:
    if nb_slots == 4:
        return [1, 4, 2, 3]
    if nb_slots == 8:
        return [1, 8, 4, 5, 3, 6, 2, 7]
    if nb_slots == 16:
        return [1, 16, 8, 9, 5, 12, 4, 13, 3, 14, 6, 11, 7, 10, 2, 15]
    raise ErreurSeeding(f"nb_slots invalide: {nb_slots}")
