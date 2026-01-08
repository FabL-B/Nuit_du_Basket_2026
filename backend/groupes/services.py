from __future__ import annotations

from typing import List, Sequence

from django.db import transaction

from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe, GroupeEquipe
from phases.models import SousPhase


class ErreurGenerationGroupes(ValueError):
    pass


def _calculer_tailles_groupes_v2(nb_equipes: int) -> List[int]:
    """
    Nouvelles règles de groupes :
    - minimum 8 équipes
    - aucun groupe de 3
    - 8  -> 4/4
    - 9  -> 4/5
    - 10 -> 5/5
    - 11 -> interdit
    - >=12 -> groupes de 4 et 5 uniquement, en favorisant 4 quand possible
    """
    if nb_equipes < 8:
        raise ErreurGenerationGroupes("Génération impossible : minimum 8 équipes requises.")
    if nb_equipes == 11:
        raise ErreurGenerationGroupes(
            "Génération impossible : 11 équipes n'est pas autorisé (inscriptions à refuser tant que 12 non atteintes)."
        )

    if nb_equipes == 8:
        return [4, 4]
    if nb_equipes == 9:
        return [4, 5]
    if nb_equipes == 10:
        return [5, 5]

    # nb_equipes >= 12 : résoudre 4*a + 5*b = nb_equipes, en maximisant a (favoriser les groupes de 4)
    for a in range(nb_equipes // 4, -1, -1):
        reste = nb_equipes - 4 * a
        if reste >= 0 and reste % 5 == 0:
            b = reste // 5
            tailles = [4] * a + [5] * b
            # sécurité: uniquement 4 et 5
            if all(t in {4, 5} for t in tailles) and sum(tailles) == nb_equipes:
                return tailles

    raise ErreurGenerationGroupes(
        f"Aucune répartition valide trouvée pour {nb_equipes} équipes (groupes de 4 et 5 uniquement)."
    )


def _creer_groupes_et_affectations(
    sous_phase: SousPhase, equipes: Sequence[Equipe]
) -> List[Groupe]:
    nb_equipes = len(equipes)
    tailles = _calculer_tailles_groupes_v2(nb_equipes)

    groupes_crees: List[Groupe] = []
    index_equipe = 0

    for idx, taille in enumerate(tailles):
        groupe = Groupe.objects.create(
            sous_phase=sous_phase,
            code=chr(ord("A") + idx),
        )
        groupes_crees.append(groupe)

        for _ in range(taille):
            GroupeEquipe.objects.create(
                groupe=groupe,
                equipe=equipes[index_equipe],
            )
            index_equipe += 1

    return groupes_crees


@transaction.atomic
def generer_groupes_pour_sous_phase(sous_phase: SousPhase) -> List[Groupe]:
    """
    Génère automatiquement les groupes pour une sous-phase donnée.
    (comportement historique Phase 1 : toutes les équipes validées du tournoi)
    Protection anti-doublon : refuse si des groupes existent déjà pour la sous-phase.
    """
    if sous_phase.groupes.exists():
        raise ErreurGenerationGroupes(
            "Des groupes existent déjà pour cette sous-phase. Suppression manuelle requise avant régénération."
        )

    equipes = list(
        Equipe.objects.filter(
            edition=sous_phase.phase_globale.edition,
            tournoi=sous_phase.tournoi,
            statut=StatutEquipe.VALIDEE,
        ).order_by("id")
    )

    return _creer_groupes_et_affectations(sous_phase, equipes)


@transaction.atomic
def generer_groupes_pour_sous_phase_avec_equipes(
    sous_phase: SousPhase,
    equipe_ids: list[int],
) -> List[Groupe]:
    """
    Génère les groupes pour une sous-phase à partir d'une liste explicite d'équipes (Phase 2).
    Protection anti-doublon : refuse si des groupes existent déjà pour la sous-phase.
    """
    if sous_phase.groupes.exists():
        raise ErreurGenerationGroupes(
            "Des groupes existent déjà pour cette sous-phase. Suppression manuelle requise avant régénération."
        )

    if not equipe_ids:
        return []

    equipes = list(
        Equipe.objects.filter(
            id__in=equipe_ids,
            edition=sous_phase.phase_globale.edition,
            tournoi=sous_phase.tournoi,
            statut=StatutEquipe.VALIDEE,
        ).order_by("id")
    )

    if len(equipes) != len(set(equipe_ids)):
        raise ErreurGenerationGroupes(
            "Liste d'équipes invalide : certaines équipes sont introuvables."
        )

    return _creer_groupes_et_affectations(sous_phase, equipes)
