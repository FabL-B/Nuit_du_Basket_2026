from __future__ import annotations

from django.db import transaction

from phases.models import PhaseGlobale, SousPhase
from phases.services._shared import branches_attendues, tournois_attendus_pour_edition


class ErreurGenerationSousPhases(ValueError):
    pass


@transaction.atomic
def generer_sous_phases_pour_phase_globale(phase_globale: PhaseGlobale) -> list[SousPhase]:
    """
    Génère les SousPhase attendues pour une PhaseGlobale.

    Comportement :
    - refuse si des sous-phases existent déjà (protection anti-doublon)
    """
    if phase_globale.sous_phases.exists():
        raise ErreurGenerationSousPhases(
            "Des sous-phases existent déjà pour cette phase globale. "
            "Suppression manuelle requise avant régénération."
        )

    return assurer_sous_phases_pour_phase_globale(phase_globale)


@transaction.atomic
def assurer_sous_phases_pour_phase_globale(phase_globale: PhaseGlobale) -> list[SousPhase]:
    """
    Version idempotente : crée les sous-phases manquantes via get_or_create
    et retourne la liste complète attendue.
    """
    tournois = tournois_attendus_pour_edition(phase_globale)
    branches = branches_attendues(phase_globale.type_phase)

    resultat: list[SousPhase] = []
    for tournoi in tournois:
        for branche in branches:
            sp, _ = SousPhase.objects.get_or_create(
                phase_globale=phase_globale,
                tournoi=tournoi,
                branche=branche,
            )
            resultat.append(sp)

    return resultat
