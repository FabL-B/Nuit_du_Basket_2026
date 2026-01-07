from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from django.db import transaction
from django.db.models import Q

from groupes.models import Groupe, GroupeEquipe
from matchs.models import Match, StatutMatch
from phases.models import PhaseGlobale


class ErreurGenerationMatchs(ValueError):
    pass


@dataclass(frozen=True)
class ResumeGenerationMatchs:
    matchs_crees: int
    groupes_traites: int


def _normaliser_paire(id_a: int, id_b: int) -> tuple[int, int]:
    return (id_a, id_b) if id_a < id_b else (id_b, id_a)


@transaction.atomic
def generer_matchs_pour_phase_globale(phase_globale: PhaseGlobale) -> ResumeGenerationMatchs:
    """
    Génère les matchs pour tous les groupes de toutes les sous-phases de la phase globale.
    - crée les matchs avec statut A_PLANIFIER
    - creneau/terrain restent NULL
    - empêche doublons (y compris inversés)
    """
    groupes = list(
        Groupe.objects.filter(sous_phase__phase_globale=phase_globale)
        .select_related("sous_phase", "sous_phase__tournoi", "sous_phase__phase_globale")
        .order_by("id")
    )
    if not groupes:
        raise ErreurGenerationMatchs("Aucun groupe trouvé pour cette phase globale.")

    # Sécurité anti-regénération : si déjà des matchs pour cette phase -> refuser
    if Match.objects.filter(phase_globale=phase_globale).exists():
        raise ErreurGenerationMatchs(
            "Des matchs existent déjà pour cette phase globale. Suppression manuelle requise avant régénération."
        )

    matchs_a_creer: list[Match] = []
    nb_groupes = 0

    for groupe in groupes:
        # équipes du groupe
        equipe_ids = list(
            GroupeEquipe.objects.filter(groupe=groupe)
            .values_list("equipe_id", flat=True)
            .order_by("equipe_id")
        )

        if len(equipe_ids) < 2:
            raise ErreurGenerationMatchs(
                f"Groupe {groupe.code} invalide : moins de 2 équipes."
            )

        nb_groupes += 1

        # toutes les paires uniques (non ordonnées)
        for id1, id2 in combinations(equipe_ids, 2):
            a_id, b_id = _normaliser_paire(id1, id2)

            matchs_a_creer.append(
                Match(
                    edition=phase_globale.edition,
                    phase_globale=phase_globale,
                    sous_phase=groupe.sous_phase,
                    groupe=groupe,
                    equipe_a_id=a_id,
                    equipe_b_id=b_id,
                    statut=StatutMatch.A_PLANIFIER,
                    creneau=None,
                    terrain=None,
                )
            )

    # Vérif doublons internes (sécurité)
    seen = set()
    for m in matchs_a_creer:
        key = (m.groupe_id, m.equipe_a_id, m.equipe_b_id)
        if key in seen:
            raise ErreurGenerationMatchs("Doublon interne détecté lors de la génération.")
        seen.add(key)

    Match.objects.bulk_create(matchs_a_creer)

    return ResumeGenerationMatchs(matchs_crees=len(matchs_a_creer), groupes_traites=nb_groupes)
