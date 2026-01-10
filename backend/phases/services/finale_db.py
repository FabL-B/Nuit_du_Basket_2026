from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from django.db import transaction

from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match, StatutMatch
from phases.models import PhaseGlobale, SousPhase
from phases.services.finale_seeding import generer_paires_premier_tour



class ErreurPhaseFinaleDB(Exception):
    pass


@dataclass(frozen=True)
class ResumeFinaleDB:
    matchs_crees: int


def _validate_ids(equipe_ids: list[int]) -> None:
    n = len(equipe_ids)
    if n not in (4, 8, 16):
        raise ErreurPhaseFinaleDB(
            "Phase finale: taille invalide. Attendu exactement 4, 8 ou 16 équipes."
        )
    if len(set(equipe_ids)) != n:
        raise ErreurPhaseFinaleDB("Phase finale: doublons d'équipes interdits.")


@transaction.atomic
def generer_matchs_phase_finale(
    phase_globale_finale: PhaseGlobale,
    sous_phase_finale: SousPhase,
    equipe_ids: Iterable[int],
) -> ResumeFinaleDB:
    """
    Crée en DB les matchs du 1er tour de la phase finale (demis/quarts/huitièmes).

    Règles:
    - N équipes doit être exactement 4, 8 ou 16 (décision admin)
    - pas de doublons
    - équipes VALIDEE
    - même édition + même tournoi que sous_phase_finale
    - anti-doublon : refuse si des matchs existent déjà pour cette sous-phase finale
    - on crée uniquement le 1er tour => N/2 matchs, sans groupe, sans planning
    """
    equipe_ids = list(equipe_ids)
    _validate_ids(equipe_ids)

    if sous_phase_finale.phase_globale_id != phase_globale_finale.id:
        raise ErreurPhaseFinaleDB("Sous-phase finale incohérente avec la phase globale finale.")

    # anti-doublon process
    if Match.objects.filter(phase_globale=phase_globale_finale, sous_phase=sous_phase_finale).exists():
        raise ErreurPhaseFinaleDB("Phase finale: des matchs existent déjà pour cette sous-phase.")

    # Charger + valider équipes
    equipes = list(
        Equipe.objects.filter(id__in=equipe_ids)
        .select_related("edition", "tournoi")
        .only("id", "edition_id", "tournoi_id", "statut")
    )
    if len(equipes) != len(equipe_ids):
        raise ErreurPhaseFinaleDB("Phase finale: au moins une équipe est introuvable.")

    # Remettre dans l'ordre demandé par l'admin
    by_id = {e.id: e for e in equipes}
    ordered = [by_id[eid] for eid in equipe_ids]

    edition_id = phase_globale_finale.edition_id
    tournoi_id = sous_phase_finale.tournoi_id

    for e in ordered:
        if e.statut != StatutEquipe.VALIDEE:
            raise ErreurPhaseFinaleDB("Phase finale: toutes les équipes doivent être VALIDEE.")
        if e.edition_id != edition_id:
            raise ErreurPhaseFinaleDB("Phase finale: équipe d'une autre édition.")
        if e.tournoi_id != tournoi_id:
            raise ErreurPhaseFinaleDB("Phase finale: équipe d'un autre tournoi.")

    # Pairing bracket classique (standard seeding)
    # Convention: l'admin fournit equipe_ids triés par seed (seed1, seed2, ...)
    paires = generer_paires_premier_tour([str(e.id) for e in ordered])

    # map string id -> Equipe
    by_id_str = {str(e.id): e for e in ordered}

    to_create: list[Match] = []
    for a_id, b_id in paires:
        ea = by_id_str[a_id]
        eb = by_id_str[b_id]
        to_create.append(
            Match(
                edition_id=edition_id,
                phase_globale=phase_globale_finale,
                sous_phase=sous_phase_finale,
                groupe=None,
                equipe_a=ea,
                equipe_b=eb,
                statut=StatutMatch.A_PLANIFIER,
                creneau=None,
                terrain=None,
            )
        )


    Match.objects.bulk_create(to_create)

    return ResumeFinaleDB(matchs_crees=len(to_create))
