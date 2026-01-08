from __future__ import annotations

from dataclasses import dataclass

from classements.models import Classement
from matchs.models import Match, StatutMatch


@dataclass
class MiniStats:
    points: int = 0
    diff: int = 0
    points_pour: int = 0


def _key_admin(rang_manuel: int | None) -> int:
    # None = pas de décision => passe après tout
    return rang_manuel if rang_manuel is not None else 10**9


def _departager_par_confrontation_directe(groupe_id: int, equipe_a_id: int, equipe_b_id: int) -> int | None:
    """
    Retourne l'équipe gagnante si on peut départager, sinon None.
    """
    matchs = list(
        Match.objects.filter(
            groupe_id=groupe_id,
            equipe_a_id__in=[equipe_a_id, equipe_b_id],
            equipe_b_id__in=[equipe_a_id, equipe_b_id],
        )
        .select_related("score")
        .order_by("id")
    )
    if not matchs:
        return None

    m = matchs[0]  # en phase de groupe, 1 match attendu entre 2 équipes

    if m.statut == StatutMatch.FORFAIT_A:
        return m.equipe_b_id
    if m.statut == StatutMatch.FORFAIT_B:
        return m.equipe_a_id
    if m.statut == StatutMatch.DOUBLE_FORFAIT:
        return None

    if m.statut != StatutMatch.TERMINE:
        return None

    try:
        score = m.score
    except Exception:
        return None

    if score.valide_le is None:
        return None

    if score.points_a > score.points_b:
        return m.equipe_a_id
    if score.points_b > score.points_a:
        return m.equipe_b_id

    return None  # égalité => manuel


def ordonner_classement_groupe(groupe) -> list[Classement]:
    """
    Tri officiel :
    1) points_classement desc
    2) différence desc
    3) points marqués desc
    4) confrontation directe uniquement si égalité à 2
    5) rang_manuel (admin) en dernier recours
    """
    rows = list(Classement.objects.filter(groupe=groupe).select_related("equipe"))
    if not rows:
        return []

    # tri de base + manuel en dernier
    rows.sort(
        key=lambda c: (
            -c.points_classement,
            -c.difference,
            -c.points_marques,
            _key_admin(c.rang_manuel),
            c.equipe.nom,
        )
    )

    def bucket_key(c: Classement):
        return (c.points_classement, c.difference, c.points_marques)

    i = 0
    while i < len(rows):
        j = i + 1
        while j < len(rows) and bucket_key(rows[j]) == bucket_key(rows[i]):
            j += 1

        bloc = rows[i:j]

        # Seulement si égalité à 2 : confrontation directe
        if len(bloc) == 2:
            a, b = bloc[0], bloc[1]
            gagnant_id = _departager_par_confrontation_directe(groupe.id, a.equipe_id, b.equipe_id)
            if gagnant_id is not None and gagnant_id == b.equipe_id:
                rows[i], rows[i + 1] = rows[i + 1], rows[i]

        # Si égalité à >=3 : rien à faire ici -> manuel
        # (le tri de base inclut déjà rang_manuel)

        i = j

    return rows
