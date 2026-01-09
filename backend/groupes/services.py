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


def _calculer_tailles_groupes_phase2(nb_equipes: int) -> list[int]:
    """
    Phase 2 : groupes de 3/4/5 autorisés.
    On accepte un seul groupe si l'effectif est faible.

    Règles simples et déterministes :
    - nb < 3 : génération impossible (un groupe doit avoir au moins 3 équipes)
    - 3..5 : 1 groupe
    - 6 : 3/3
    - 7 : 3/4
    - 8 : 4/4
    - 9 : 4/5
    - 10 : 5/5
    - 11 : 3/4/4
    - 12 : 4/4/4
    - 13 : 4/4/5
    - 14 : 4/5/5
    - 15 : 5/5/5
    - au-delà : on boucle en privilégiant 5 puis 4 puis 3.
    """
    if nb_equipes < 3:
        raise ErreurGenerationGroupes("Génération impossible : minimum 3 équipes requis en Phase 2.")

    # Cas simples (les plus fréquents en Phase 2)
    mapping = {
        3: [3],
        4: [4],
        5: [5],
        6: [3, 3],
        7: [3, 4],
        8: [4, 4],
        9: [4, 5],
        10: [5, 5],
        11: [3, 4, 4],
        12: [4, 4, 4],
        13: [4, 4, 5],
        14: [4, 5, 5],
        15: [5, 5, 5],
    }
    if nb_equipes in mapping:
        return mapping[nb_equipes]

    # Fallback générique (rare en Phase 2, mais propre)
    tailles: list[int] = []
    reste = nb_equipes
    while reste > 0:
        if reste >= 5:
            # éviter de finir avec 1 ou 2
            if reste in (6, 7, 8):
                # gérés plus haut normalement, mais sécurise
                break
            tailles.append(5)
            reste -= 5
        elif reste == 4:
            tailles.append(4)
            reste -= 4
        elif reste == 3:
            tailles.append(3)
            reste -= 3
        else:
            # ici reste vaut 1 ou 2 => on rééquilibre
            raise ErreurGenerationGroupes(
                "Génération Phase 2 impossible : répartition incohérente (reste 1 ou 2)."
            )
    # si on a cassé plus haut
    if reste != 0:
        return mapping[reste] if reste in mapping else tailles

    return tailles


def _creer_groupes_et_affectations(
    sous_phase: SousPhase,
    equipes: list[Equipe],
    tailles: list[int] | None = None,
) -> list[Groupe]:
    """
    Crée les groupes + affectations (GroupeEquipe) pour une sous-phase.

    - Si tailles est None : on applique la règle Phase 1 v2 (min 8, 4/5, etc.)
    - Si tailles est fourni : on utilise ces tailles (ex: Phase 2 = 3/4/5 autorisés)
    """
    nb_equipes = len(equipes)

    if tailles is None:
        # Comportement historique Phase 1 (tes tests existants)
        tailles = _calculer_tailles_groupes_v2(nb_equipes)
    else:
        # Sécurité : cohérence simple
        if sum(tailles) != nb_equipes:
            raise ErreurGenerationGroupes(
                f"Répartition invalide : {sum(tailles)} places pour {nb_equipes} équipes."
            )

    groupes_crees: list[Groupe] = []
    index_equipe = 0

    for idx, taille in enumerate(tailles):
        g = Groupe.objects.create(
            sous_phase=sous_phase,
            code=chr(ord("A") + idx),
        )
        groupes_crees.append(g)

        for _ in range(taille):
            GroupeEquipe.objects.create(
                groupe=g,
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


@transaction.atomic
def generer_groupes_phase2_pour_sous_phase_avec_equipes(
    sous_phase: SousPhase,
    equipe_ids: list[int],
) -> list[Groupe]:
    if sous_phase.groupes.exists():
        raise ErreurGenerationGroupes(
            "Des groupes existent déjà pour cette sous-phase. Suppression manuelle requise avant régénération."
        )

    equipes = list(
        Equipe.objects.filter(id__in=equipe_ids).order_by("id")
    )
    nb_equipes = len(equipes)
    tailles = _calculer_tailles_groupes_phase2(nb_equipes)

    return _creer_groupes_et_affectations(sous_phase, equipes, tailles=tailles)
