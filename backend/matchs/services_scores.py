from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from matchs.models import Match, Score, StatutMatch
from phases.models import TypePhaseGlobale
from classements.services import recalculer_classements_pour_groupe
from phases.services.finale_progression import avancer_bracket_si_possible


class ErreurScore(ValueError):
    pass


@transaction.atomic
def saisir_score(match: Match, points_a: int, points_b: int) -> Score:
    """
    Crée ou met à jour un score non validé.
    Interdit si match terminé/forfait, ou si score déjà validé.
    """
    if match.statut in {
        StatutMatch.TERMINE,
        StatutMatch.FORFAIT_A,
        StatutMatch.FORFAIT_B,
        StatutMatch.DOUBLE_FORFAIT,
    }:
        raise ErreurScore("Impossible de saisir un score sur un match terminé ou forfait.")

    score, created = Score.objects.get_or_create(
        match=match,
        defaults={"points_a": points_a, "points_b": points_b},
    )
    if not created:
        if score.valide_le is not None:
            raise ErreurScore("Score déjà validé : modification interdite.")
        score.points_a = points_a
        score.points_b = points_b
        score.save(update_fields=["points_a", "points_b", "modifie_le"])
    return score


@transaction.atomic
def valider_score(match, utilisateur) -> Score:
    """
    Valide le score existant du match.
    IMPORTANT : l'ordre est contractuel :
    1) valider le Score (valide_le + valide_par)
    2) passer le Match en TERMINE
    3) recalculer le classement (si match de groupe)
    4) si match de phase finale -> tenter de créer le match suivant
    """
    if match.statut in {StatutMatch.FORFAIT_A, StatutMatch.FORFAIT_B, StatutMatch.DOUBLE_FORFAIT}:
        raise ErreurScore("Impossible de valider un score sur un match forfait.")

    try:
        score = match.score
    except Score.DoesNotExist:
        raise ErreurScore("Aucun score saisi pour ce match.")

    if score.valide_le is not None:
        raise ErreurScore("Score déjà validé.")

    # 1) Valider le score
    score.valide_le = timezone.now()
    score.valide_par = utilisateur
    score.save(update_fields=["valide_le", "valide_par", "modifie_le"])

    # 2) Terminer le match
    match.statut = StatutMatch.TERMINE
    match.save(update_fields=["statut", "modifie_le"])

    # 3) Recalcul classement (seulement si match de groupe)
    if match.groupe_id:
        recalculer_classements_pour_groupe(match.groupe)

    # 4) Phase finale: créer le match suivant si possible
    if match.phase_globale.type_phase == TypePhaseGlobale.FINALE:
        from phases.services.finale_progression import avancer_bracket_si_possible

        avancer_bracket_si_possible(match)

    return score
