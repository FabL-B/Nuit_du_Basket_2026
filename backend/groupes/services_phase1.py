from __future__ import annotations

from django.db import transaction

from inscriptions.models import Equipe, StatutEquipe
from phases.models import SousPhase
from .services_shared import ErreurGenerationGroupes, _creer_groupes_et_affectations


def _calculer_tailles_groupes_phase1(nb_equipes: int) -> list[int]:
    """
    Phase 1 :
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

    for a in range(nb_equipes // 4, -1, -1):
        reste = nb_equipes - 4 * a
        if reste >= 0 and reste % 5 == 0:
            b = reste // 5
            tailles = [4] * a + [5] * b
            if all(t in {4, 5} for t in tailles) and sum(tailles) == nb_equipes:
                return tailles

    raise ErreurGenerationGroupes(
        f"Aucune répartition valide trouvée pour {nb_equipes} équipes (groupes de 4 et 5 uniquement)."
    )


@transaction.atomic
def generer_groupes_phase1_pour_sous_phase(sous_phase: SousPhase) -> list:
    """
    Phase 1 : toutes les équipes VALIDEE du tournoi, réparties automatiquement.
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

    tailles = _calculer_tailles_groupes_phase1(len(equipes))
    return _creer_groupes_et_affectations(sous_phase, equipes, tailles)
