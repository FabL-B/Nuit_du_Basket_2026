from __future__ import annotations

from django.db import transaction

from phases.models import (
    PhaseGlobale,
    SousPhase,
    TypePhaseGlobale,
    BrancheSousPhase,
)
from tournois.models import Tournoi, CodeTournoi


class ErreurGenerationSousPhases(ValueError):
    pass


def _branches_attendues(type_phase: str) -> list[str]:
    if type_phase == TypePhaseGlobale.PHASE_1:
        return [BrancheSousPhase.AUCUNE]
    if type_phase in {TypePhaseGlobale.PHASE_2, TypePhaseGlobale.FINALE}:
        return [BrancheSousPhase.CHALLENGE, BrancheSousPhase.CONSOLANTE]
    raise ErreurGenerationSousPhases(f"Type de phase globale inconnu: {type_phase}")


def _tournois_attendus_pour_edition(phase_globale: PhaseGlobale) -> list[Tournoi]:
    """
    Règle : une édition doit contenir les 3 tournois fixes.
    On échoue explicitement si ce n'est pas le cas.
    """
    tournois = list(Tournoi.objects.filter(edition=phase_globale.edition).order_by("code"))
    codes = {t.code for t in tournois}
    attendus = {CodeTournoi.ROOKIE, CodeTournoi.LOISIR, CodeTournoi.COMPETITEUR}

    if codes != attendus:
        raise ErreurGenerationSousPhases(
            "Tournois invalides pour cette édition. "
            "Attendu exactement: ROOKIE, LOISIR, COMPETITEUR."
        )

    # ordre stable
    ordre = {CodeTournoi.ROOKIE: 0, CodeTournoi.LOISIR: 1, CodeTournoi.COMPETITEUR: 2}
    tournois.sort(key=lambda t: ordre[t.code])
    return tournois


@transaction.atomic
def generer_sous_phases_pour_phase_globale(phase_globale: PhaseGlobale) -> list[SousPhase]:
    """
    Génère les SousPhase attendues pour une PhaseGlobale.

    Comportement :
    - Refuse de regénérer si des sous-phases existent déjà (protection contre doublons).
    """
    if phase_globale.sous_phases.exists():
        raise ErreurGenerationSousPhases(
            "Des sous-phases existent déjà pour cette phase globale. "
            "Suppression manuelle requise avant régénération."
        )

    tournois = _tournois_attendus_pour_edition(phase_globale)
    branches = _branches_attendues(phase_globale.type_phase)

    creees: list[SousPhase] = []
    for tournoi in tournois:
        for branche in branches:
            creees.append(
                SousPhase.objects.create(
                    phase_globale=phase_globale,
                    tournoi=tournoi,
                    branche=branche,
                )
            )

    return creees
