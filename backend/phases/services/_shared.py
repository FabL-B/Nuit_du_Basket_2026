from __future__ import annotations

from phases.models import BrancheSousPhase, PhaseGlobale, TypePhaseGlobale
from tournois.models import CodeTournoi, Tournoi


class ErreurReglesPhase(ValueError):
    pass


def branches_attendues(type_phase: str) -> list[str]:
    if type_phase == TypePhaseGlobale.PHASE_1:
        return [BrancheSousPhase.AUCUNE]
    if type_phase in {TypePhaseGlobale.PHASE_2, TypePhaseGlobale.FINALE}:
        return [BrancheSousPhase.CHALLENGE, BrancheSousPhase.CONSOLANTE]
    raise ErreurReglesPhase(f"Type de phase globale inconnu: {type_phase}")


def tournois_attendus_pour_edition(phase_globale: PhaseGlobale) -> list[Tournoi]:
    """
    Règle : une édition doit contenir exactement les 3 tournois fixes.
    On échoue explicitement si ce n'est pas le cas.
    """
    tournois = list(Tournoi.objects.filter(edition=phase_globale.edition).order_by("code"))
    codes = {t.code for t in tournois}
    attendus = {CodeTournoi.ROOKIE, CodeTournoi.LOISIR, CodeTournoi.COMPETITEUR}

    if codes != attendus:
        raise ErreurReglesPhase(
            "Tournois invalides pour cette édition. "
            "Attendu exactement: ROOKIE, LOISIR, COMPETITEUR."
        )

    ordre = {CodeTournoi.ROOKIE: 0, CodeTournoi.LOISIR: 1, CodeTournoi.COMPETITEUR: 2}
    tournois.sort(key=lambda t: ordre[t.code])
    return tournois
