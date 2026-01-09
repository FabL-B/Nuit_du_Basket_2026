from __future__ import annotations

from phases.models import BrancheSousPhase, PhaseGlobale, TypePhaseGlobale
from tournois.models import CodeTournoi, Tournoi


_CODES_AUTORISES = {CodeTournoi.ROOKIE, CodeTournoi.LOISIR, CodeTournoi.COMPETITEUR}


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


def branches_attendues(type_phase: str) -> list[str]:
    if type_phase == TypePhaseGlobale.PHASE_1:
        return [BrancheSousPhase.AUCUNE]
    if type_phase in {TypePhaseGlobale.PHASE_2, TypePhaseGlobale.FINALE}:
        return [BrancheSousPhase.CHALLENGE, BrancheSousPhase.CONSOLANTE]
    raise ErreurReglesPhase(f"Type de phase globale inconnu: {type_phase}")


def tournois_presents_pour_edition(phase_globale: PhaseGlobale) -> list[Tournoi]:
    """
    Version souple : retourne les tournois réellement présents dans l'édition.

    Refuse uniquement si :
    - aucun tournoi
    - code non autorisé
    - doublon de code dans l'édition
    """
    tournois = list(Tournoi.objects.filter(edition=phase_globale.edition).order_by("code"))
    if not tournois:
        raise ErreurReglesPhase("Aucun tournoi pour cette édition.")

    codes = [t.code for t in tournois]
    if any(c not in _CODES_AUTORISES for c in codes):
        raise ErreurReglesPhase("Tournois invalides : code inconnu pour cette édition.")

    if len(set(codes)) != len(codes):
        raise ErreurReglesPhase("Tournois invalides : doublon de code pour cette édition.")

    ordre = {CodeTournoi.ROOKIE: 0, CodeTournoi.LOISIR: 1, CodeTournoi.COMPETITEUR: 2}
    tournois.sort(key=lambda t: ordre[t.code])
    return tournois


def verifier_edition_a_3_tournois(phase_globale: PhaseGlobale) -> None:
    """
    Version stricte (verrou process futur) :
    exige exactement les 3 tournois.
    """
    tournois = tournois_presents_pour_edition(phase_globale)
    codes = {t.code for t in tournois}
    if codes != _CODES_AUTORISES:
        raise ErreurReglesPhase(
            "Tournois incomplets pour cette édition. "
            "Attendu: ROOKIE + LOISIR + COMPETITEUR."
        )