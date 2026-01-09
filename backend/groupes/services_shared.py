from __future__ import annotations

from django.db import transaction

from groupes.models import Groupe, GroupeEquipe
from phases.models import SousPhase
from inscriptions.models import Equipe


class ErreurGenerationGroupes(ValueError):
    pass


def _creer_groupes_et_affectations(
    sous_phase: SousPhase,
    equipes: list[Equipe],
    tailles: list[int],
) -> list[Groupe]:
    """
    Primitive unique de création :
    - crée les Groupes (A, B, C...)
    - crée les GroupeEquipe
    Hypothèse: tailles est cohérent et sum(tailles) == len(equipes)
    """
    if sum(tailles) != len(equipes):
        raise ErreurGenerationGroupes(
            f"Répartition invalide : {sum(tailles)} places pour {len(equipes)} équipes."
        )

    groupes_crees: list[Groupe] = []
    index_equipe = 0

    for idx, taille in enumerate(tailles):
        g = Groupe.objects.create(sous_phase=sous_phase, code=chr(ord("A") + idx))
        groupes_crees.append(g)

        for _ in range(taille):
            GroupeEquipe.objects.create(groupe=g, equipe=equipes[index_equipe])
            index_equipe += 1

    return groupes_crees
