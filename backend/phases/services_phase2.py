from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from classements.models import Classement
from classements.services_tri import ordonner_classement_groupe
from groupes.models import Groupe
from inscriptions.models import Equipe
from phases.models import (
    BrancheSousPhase,
    PhaseGlobale,
    SousPhase,
    StatutPhase,
    TypePhaseGlobale,
)
from tournois.models import CodeTournoi, Tournoi
from groupes.services import generer_groupes_phase2_pour_sous_phase_avec_equipes


class ErreurGenerationPhase2(ValueError):
    pass


@dataclass(frozen=True)
class PropositionRepartition:
    code_tournoi: str
    equipe_ids_ordre: list[int]
    nb_total: int
    nb_challenge_min: int  # floor(n/2)
    nb_challenge_max: int  # ceil(n/2)


@dataclass(frozen=True)
class ResumePreviewPhase2:
    phase2_id: int
    propositions: list[PropositionRepartition]
    tournois_impairs: list[str]


@dataclass(frozen=True)
class ResumeGenerationPhase2:
    phase2_id: int
    equipes_challenge: int
    equipes_consolante: int
    sous_phases_creees: int
    groupes_crees: int


def _get_phase2(edition_id: int) -> PhaseGlobale:
    phase2, _ = PhaseGlobale.objects.get_or_create(
        edition_id=edition_id,
        type_phase=TypePhaseGlobale.PHASE_2,
        sequence=1,
        defaults={"statut": StatutPhase.BROUILLON},
    )
    return phase2


def _get_or_create_sousphases_phase2(phase2: PhaseGlobale) -> None:
    tournois = list(Tournoi.objects.filter(edition=phase2.edition))
    if not tournois:
        raise ErreurGenerationPhase2("Aucun tournoi pour cette édition.")

    for t in tournois:
        for branche in (BrancheSousPhase.CHALLENGE, BrancheSousPhase.CONSOLANTE):
            SousPhase.objects.get_or_create(
                phase_globale=phase2,
                tournoi=t,
                branche=branche,
                defaults={"statut": StatutPhase.BROUILLON},
            )


def _ordre_equipes_par_tournoi_phase1(phase1: PhaseGlobale, code_tournoi: str) -> list[int]:
    # groupes Phase 1 du tournoi (branche AUCUNE)
    groupes = list(
        Groupe.objects.filter(
            sous_phase__phase_globale=phase1,
            sous_phase__tournoi__code=code_tournoi,
            sous_phase__branche=BrancheSousPhase.AUCUNE,
        ).order_by("id")
    )
    if not groupes:
        return []

    # ordre par groupe (tri officiel), puis concat 1ers/2e/3e...
    ordre_par_groupe: list[list[int]] = []
    max_len = 0

    for g in groupes:
        ordre = ordonner_classement_groupe(g)
        ids = [c.equipe_id for c in ordre]
        if not ids:
            continue
        ordre_par_groupe.append(ids)
        max_len = max(max_len, len(ids))

    resultat: list[int] = []
    for rang in range(max_len):
        for ids in ordre_par_groupe:
            if rang < len(ids):
                resultat.append(ids[rang])

    # dédoublonnage sécurité
    seen = set()
    unique = []
    for eid in resultat:
        if eid not in seen:
            unique.append(eid)
            seen.add(eid)
    return unique


def _get_sous_phase_phase2(phase2: PhaseGlobale, code_tournoi: str, branche: str) -> SousPhase:
    return SousPhase.objects.get(
        phase_globale=phase2,
        tournoi__code=code_tournoi,
        branche=branche,
    )


@transaction.atomic
def previsualiser_phase2_depuis_phase1(phase1: PhaseGlobale) -> ResumePreviewPhase2:
    if phase1.type_phase != TypePhaseGlobale.PHASE_1:
        raise ErreurGenerationPhase2("Phase source invalide : attendu Phase 1.")
    if phase1.statut != StatutPhase.CLOTUREE:
        raise ErreurGenerationPhase2("Phase 1 doit être clôturée avant prévisualisation Phase 2.")

    phase2 = _get_phase2(phase1.edition_id)
    _get_or_create_sousphases_phase2(phase2)

    propositions: list[PropositionRepartition] = []
    tournois_impairs: list[str] = []

    for code in (CodeTournoi.ROOKIE, CodeTournoi.LOISIR, CodeTournoi.COMPETITEUR):
        ordre = _ordre_equipes_par_tournoi_phase1(phase1, code)
        if not ordre:
            continue

        n = len(ordre)
        nb_min = n // 2
        nb_max = (n + 1) // 2

        if n % 2 == 1:
            tournois_impairs.append(code)

        propositions.append(
            PropositionRepartition(
                code_tournoi=code,
                equipe_ids_ordre=ordre,
                nb_total=n,
                nb_challenge_min=nb_min,
                nb_challenge_max=nb_max,
            )
        )

    return ResumePreviewPhase2(
        phase2_id=phase2.id,
        propositions=propositions,
        tournois_impairs=tournois_impairs,
    )


@transaction.atomic
def generer_phase2_depuis_phase1(
    phase1: PhaseGlobale,
    decision_impair: dict[str, str] | None = None,
) -> ResumeGenerationPhase2:
    """
    decision_impair: mapping {code_tournoi: "CHALLENGE"|"CONSOLANTE"}.
    Obligatoire si le tournoi a un nombre impair d'équipes.
    """
    preview = previsualiser_phase2_depuis_phase1(phase1)
    phase2 = PhaseGlobale.objects.get(id=preview.phase2_id)

    decision_impair = decision_impair or {}

    # Validation des choix admin pour tournois impairs
    for code in preview.tournois_impairs:
        if code not in decision_impair:
            raise ErreurGenerationPhase2(
                f"Tournoi {code} impair : décision admin requise (CHALLENGE ou CONSOLANTE)."
            )
        if decision_impair[code] not in {"CHALLENGE", "CONSOLANTE"}:
            raise ErreurGenerationPhase2(
                f"Décision invalide pour {code} : attendu CHALLENGE ou CONSOLANTE."
            )

    total_challenge = 0
    total_consolante = 0
    groupes_crees = 0

    for prop in preview.propositions:
        ordre = prop.equipe_ids_ordre
        n = prop.nb_total

        if n % 2 == 0:
            nb_challenge = n // 2
        else:
            # choix admin : qui a l'équipe en plus
            if decision_impair[prop.code_tournoi] == "CHALLENGE":
                nb_challenge = (n + 1) // 2
            else:
                nb_challenge = n // 2  # l'équipe en plus va en consolante

        ids_challenge = ordre[:nb_challenge]
        ids_consolante = ordre[nb_challenge:]

        sp_challenge = _get_sous_phase_phase2(phase2, prop.code_tournoi, BrancheSousPhase.CHALLENGE)
        sp_consolante = _get_sous_phase_phase2(
            phase2, prop.code_tournoi, BrancheSousPhase.CONSOLANTE
        )

        # Créer les groupes Phase 2
        groupes_ch = generer_groupes_phase2_pour_sous_phase_avec_equipes(sp_challenge, ids_challenge)
        groupes_co = generer_groupes_phase2_pour_sous_phase_avec_equipes(sp_consolante, ids_consolante)

        groupes_crees += len(groupes_ch) + len(groupes_co)

        total_challenge += len(ids_challenge)
        total_consolante += len(ids_consolante)

    return ResumeGenerationPhase2(
        phase2_id=phase2.id,
        equipes_challenge=total_challenge,
        equipes_consolante=total_consolante,
        sous_phases_creees=SousPhase.objects.filter(phase_globale=phase2).count(),
        groupes_crees=groupes_crees,
    )
