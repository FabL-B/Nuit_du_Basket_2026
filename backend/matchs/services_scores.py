from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from matchs.models import Match, Score, StatutMatch


class ErreurScore(ValueError):
    pass


@transaction.atomic
def saisir_score(match: Match, points_a: int, points_b: int) -> Score:
    """
    Crée ou met à jour un score non validé.
    Interdit si match terminé/forfait, ou si score déjà validé.
    """
    if match.statut in {StatutMatch.TERMINE, StatutMatch.FORFAIT_A, StatutMatch.FORFAIT_B, StatutMatch.DOUBLE_FORFAIT}:
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
def valider_score(match: Match, utilisateur) -> Score:
    """
    Valide le score existant du match.
    Règles :
    - score doit exister
    - match ne doit pas être forfait
    - passe le match en TERMINE
    """
    if match.statut in {StatutMatch.FORFAIT_A, StatutMatch.FORFAIT_B, StatutMatch.DOUBLE_FORFAIT}:
        raise ErreurScore("Impossible de valider un score sur un match forfait.")

    try:
        score = match.score
    except Score.DoesNotExist:
        raise ErreurScore("Aucun score saisi pour ce match.")

    if score.valide_le is not None:
        raise ErreurScore("Score déjà validé.")

    score.valide_le = timezone.now()
    score.valide_par = utilisateur
    score.save(update_fields=["valide_le", "valide_par", "modifie_le"])

    match.statut = StatutMatch.TERMINE
    match.save(update_fields=["statut", "modifie_le"])

    return score
