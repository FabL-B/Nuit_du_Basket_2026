from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from django.db import transaction

from groupes.models import Groupe, GroupeEquipe
from groupes.services_phase2 import _calculer_tailles_groupes_phase2
from matchs.models import Match, StatutMatch
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase


class ErreurGenerationMatchsTheoriquesPhase2(ValueError):
    pass


@dataclass(frozen=True)
class ParticipantTheoriquePhase2:
    groupe_phase1_id: int
    groupe_code: str
    tournoi_code: str
    rang_phase1: int
    branche: str
    libelle: str


@dataclass(frozen=True)
class GroupeTheoriquePhase2:
    code: str
    participants: list[ParticipantTheoriquePhase2]


@dataclass(frozen=True)
class ResumeGenerationMatchsTheoriquesPhase2:
    matchs_crees: int
    groupes_challenge: int
    groupes_consolante: int


def construire_participants_theoriques_phase2(
    groupes_phase1: list[Groupe],
) -> tuple[list[ParticipantTheoriquePhase2], list[ParticipantTheoriquePhase2]]:
    """
    À partir des groupes de phase 1, construit deux listes de participants théoriques :
    - Challenge : top 50% (arrondi à l'inférieur)
    - Consolante : le reste
    """
    challenge: list[ParticipantTheoriquePhase2] = []
    consolante: list[ParticipantTheoriquePhase2] = []

    for groupe in groupes_phase1:
        participants = list(
            GroupeEquipe.objects.filter(groupe=groupe)
            .select_related("groupe", "groupe__sous_phase", "groupe__sous_phase__tournoi")
            .order_by("position_groupe")
        )

        taille = len(participants)
        if taille < 2:
            continue

        top_count = taille // 2
        tournoi_code = groupe.sous_phase.tournoi.code

        for rang in range(1, taille + 1):
            branche = (
                BrancheSousPhase.CHALLENGE
                if rang <= top_count
                else BrancheSousPhase.CONSOLANTE
            )

            item = ParticipantTheoriquePhase2(
                groupe_phase1_id=groupe.id,
                groupe_code=groupe.code,
                tournoi_code=tournoi_code,
                rang_phase1=rang,
                branche=branche,
                libelle=f"{tournoi_code} - Groupe {groupe.code} - Rang {rang}",
            )

            if branche == BrancheSousPhase.CHALLENGE:
                challenge.append(item)
            else:
                consolante.append(item)

    return challenge, consolante


def repartir_participants_en_groupes_theoriques(
    participants: list[ParticipantTheoriquePhase2],
    tailles: list[int],
) -> list[GroupeTheoriquePhase2]:
    groupes: list[GroupeTheoriquePhase2] = []
    index = 0

    for idx, taille in enumerate(tailles):
        code = chr(ord("A") + idx)
        subset = participants[index:index + taille]
        groupes.append(
            GroupeTheoriquePhase2(
                code=code,
                participants=subset,
            )
        )
        index += taille

    return groupes


@transaction.atomic
def generer_matchs_theoriques_phase2(
    phase_globale_phase2: PhaseGlobale,
) -> ResumeGenerationMatchsTheoriquesPhase2:
    """
    Génère les matchs théoriques de phase 2 :
    - à partir des groupes de phase 1 de la même édition
    - par tournoi
    - séparément pour les branches Challenge / Consolante
    - en mini round-robin dans des groupes théoriques
    """
    if phase_globale_phase2.type_phase != TypePhaseGlobale.PHASE_2:
        raise ErreurGenerationMatchsTheoriquesPhase2(
            "La phase fournie n'est pas une PHASE_2."
        )

    if Match.objects.filter(phase_globale=phase_globale_phase2).exists():
        raise ErreurGenerationMatchsTheoriquesPhase2(
            "Des matchs existent déjà pour cette phase globale."
        )

    sous_phases = list(
        SousPhase.objects.filter(phase_globale=phase_globale_phase2)
        .select_related("tournoi")
        .order_by("tournoi_id", "branche", "id")
    )
    if not sous_phases:
        raise ErreurGenerationMatchsTheoriquesPhase2(
            "Aucune sous-phase trouvée pour la phase 2."
        )

    matchs_a_creer: list[Match] = []
    nb_groupes_challenge = 0
    nb_groupes_consolante = 0

    for sous_phase in sous_phases:
        if sous_phase.branche not in (
            BrancheSousPhase.CHALLENGE,
            BrancheSousPhase.CONSOLANTE,
        ):
            continue

        groupes_phase1 = list(
            Groupe.objects.filter(
                sous_phase__phase_globale__edition=phase_globale_phase2.edition,
                sous_phase__phase_globale__type_phase=TypePhaseGlobale.PHASE_1,
                sous_phase__tournoi=sous_phase.tournoi,
            )
            .select_related("sous_phase", "sous_phase__tournoi")
            .order_by("id")
        )

        if not groupes_phase1:
            continue

        participants_challenge, participants_consolante = (
            construire_participants_theoriques_phase2(groupes_phase1)
        )

        if sous_phase.branche == BrancheSousPhase.CHALLENGE:
            participants = participants_challenge
        else:
            participants = participants_consolante

        if len(participants) < 3:
            raise ErreurGenerationMatchsTheoriquesPhase2(
                f"Pas assez de participants pour la sous-phase {sous_phase.id} ({sous_phase.branche})."
            )

        tailles = _calculer_tailles_groupes_phase2(len(participants))
        groupes_theoriques = repartir_participants_en_groupes_theoriques(participants, tailles)

        if sous_phase.branche == BrancheSousPhase.CHALLENGE:
            nb_groupes_challenge += len(groupes_theoriques)
        else:
            nb_groupes_consolante += len(groupes_theoriques)

        for groupe_theorique in groupes_theoriques:
            for p1, p2 in combinations(groupe_theorique.participants, 2):
                matchs_a_creer.append(
                    Match(
                        edition=phase_globale_phase2.edition,
                        phase_globale=phase_globale_phase2,
                        sous_phase=sous_phase,
                        groupe=None,
                        equipe_a=None,
                        equipe_b=None,
                        libelle_equipe_a=p1.libelle,
                        libelle_equipe_b=p2.libelle,
                        statut=StatutMatch.A_PLANIFIER,
                        creneau=None,
                        terrain=None,
                    )
                )

    Match.objects.bulk_create(matchs_a_creer)

    return ResumeGenerationMatchsTheoriquesPhase2(
        matchs_crees=len(matchs_a_creer),
        groupes_challenge=nb_groupes_challenge,
        groupes_consolante=nb_groupes_consolante,
    )
