from __future__ import annotations

from django.db import transaction

from inscriptions.models import Equipe, StatutEquipe
from phases.models import SousPhase
from .services_shared import ErreurGenerationGroupes, _creer_groupes_et_affectations


def _calculer_tailles_groupes_phase2(nb_equipes: int) -> list[int]:
    """
    Phase 2 : groupes de 3/4/5 autorisés.
    """
    if nb_equipes < 3:
        raise ErreurGenerationGroupes("Génération impossible : minimum 3 équipes requis en Phase 2.")

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

    tailles: list[int] = []
    reste = nb_equipes
    while reste > 0:
        if reste >= 5 and reste not in (6, 7, 8):
            tailles.append(5)
            reste -= 5
        elif reste == 4:
            tailles.append(4)
            reste -= 4
        elif reste == 3:
            tailles.append(3)
            reste -= 3
        else:
            raise ErreurGenerationGroupes(
                "Génération Phase 2 impossible : répartition incohérente (reste 1 ou 2)."
            )

    return tailles


@transaction.atomic
def generer_groupes_phase2_pour_sous_phase_avec_equipes(
    sous_phase: SousPhase,
    equipe_ids: list[int],
) -> list:
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
        raise ErreurGenerationGroupes("Liste d'équipes invalide : certaines équipes sont introuvables.")

    tailles = _calculer_tailles_groupes_phase2(len(equipes))
    return _creer_groupes_et_affectations(sous_phase, equipes, tailles)
