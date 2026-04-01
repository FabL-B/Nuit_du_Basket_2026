from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from django.db import transaction

from groupes.models import Groupe, GroupeEquipe
from matchs.models import Match, StatutMatch
from phases.models import PhaseGlobale


class ErreurGenerationMatchsTheoriques(ValueError):
    pass


@dataclass(frozen=True)
class ResumeGenerationMatchsTheoriques:
    matchs_crees: int
    groupes_traites: int


def _libelle_participant(groupe: Groupe, position_groupe: int) -> str:
    tournoi_code = groupe.sous_phase.tournoi.code
    return f"{tournoi_code} - Groupe {groupe.code} - Place {position_groupe}"


@transaction.atomic
def generer_matchs_theoriques_phase1(
    phase_globale: PhaseGlobale,
) -> ResumeGenerationMatchsTheoriques:
    """
    Génère les matchs théoriques de phase 1 pour tous les groupes
    de toutes les sous-phases de la phase globale.

    - crée des matchs sans équipes réelles
    - renseigne libelle_equipe_a / libelle_equipe_b
    - creneau/terrain restent NULL
    - empêche la régénération si des matchs existent déjà
    """
    groupes = list(
        Groupe.objects.filter(sous_phase__phase_globale=phase_globale)
        .select_related(
            "sous_phase",
            "sous_phase__tournoi",
            "sous_phase__phase_globale",
        )
        .order_by("id")
    )

    if not groupes:
        raise ErreurGenerationMatchsTheoriques(
            "Aucun groupe trouvé pour cette phase globale."
        )

    if Match.objects.filter(phase_globale=phase_globale).exists():
        raise ErreurGenerationMatchsTheoriques(
            "Des matchs existent déjà pour cette phase globale. "
            "Suppression manuelle requise avant régénération."
        )

    matchs_a_creer: list[Match] = []
    nb_groupes = 0

    for groupe in groupes:
        participants = list(
            GroupeEquipe.objects.filter(groupe=groupe)
            .order_by("position_groupe")
        )

        if len(participants) < 2:
            raise ErreurGenerationMatchsTheoriques(
                f"Groupe {groupe.code} invalide : moins de 2 équipes."
            )

        positions = [ge.position_groupe for ge in participants]
        nb_groupes += 1

        for pos_a, pos_b in combinations(positions, 2):
            libelle_a = _libelle_participant(groupe, pos_a)
            libelle_b = _libelle_participant(groupe, pos_b)

            matchs_a_creer.append(
                Match(
                    edition=phase_globale.edition,
                    phase_globale=phase_globale,
                    sous_phase=groupe.sous_phase,
                    groupe=groupe,
                    equipe_a=None,
                    equipe_b=None,
                    libelle_equipe_a=libelle_a,
                    libelle_equipe_b=libelle_b,
                    statut=StatutMatch.A_PLANIFIER,
                    creneau=None,
                    terrain=None,
                )
            )

    Match.objects.bulk_create(matchs_a_creer)

    return ResumeGenerationMatchsTheoriques(
        matchs_crees=len(matchs_a_creer),
        groupes_traites=nb_groupes,
    )
