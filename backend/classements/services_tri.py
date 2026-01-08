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


def _matches_finalises_entre(groupe_id: int, equipe_ids: list[int]) -> list[Match]:
    return list(
        Match.objects.filter(
            groupe_id=groupe_id,
            equipe_a_id__in=equipe_ids,
            equipe_b_id__in=equipe_ids,
        )
        .exclude(statut=StatutMatch.A_PLANIFIER)
        .exclude(statut=StatutMatch.PLANIFIE)
        .select_related("score")
        .order_by("id")
    )


def _appliquer_resultat_mini(stats: dict[int, MiniStats], match: Match) -> None:
    a = match.equipe_a_id
    b = match.equipe_b_id

    # Forfaits : pas de points marqués/encaissés (non défini), mais points classement OK
    if match.statut == StatutMatch.FORFAIT_A:
        stats[a].points += 0
        stats[b].points += 3
        stats[a].diff += 0
        stats[b].diff += 0
        return
    if match.statut == StatutMatch.FORFAIT_B:
        stats[b].points += 0
        stats[a].points += 3
        stats[a].diff += 0
        stats[b].diff += 0
        return
    if match.statut == StatutMatch.DOUBLE_FORFAIT:
        stats[a].points += 0
        stats[b].points += 0
        stats[a].diff += 0
        stats[b].diff += 0
        return

    # Match terminé avec score validé uniquement
    if match.statut != StatutMatch.TERMINE:
        return
    try:
        score = match.score
    except Exception:
        return
    if score.valide_le is None:
        return

    pa = score.points_a
    pb = score.points_b

    stats[a].points_pour += pa
    stats[b].points_pour += pb
    stats[a].diff += pa - pb
    stats[b].diff += pb - pa

    if pa > pb:
        stats[a].points += 3
        stats[b].points += 1
    elif pb > pa:
        stats[b].points += 3
        stats[a].points += 1
    else:
        stats[a].points += 2
        stats[b].points += 2


def _departager_par_confrontation_directe(
    groupe_id: int,
    equipe_a_id: int,
    equipe_b_id: int,
) -> int | None:
    """
    Retourne :
    - equipe_id gagnante si on peut départager
    - None sinon (pas de match, égalité, double forfait, pas de score validé)
    """
    matchs = _matches_finalises_entre(groupe_id, [equipe_a_id, equipe_b_id])
    if not matchs:
        return None

    # On prend le match unique attendu en phase de groupe
    m = matchs[0]

    if m.statut in {StatutMatch.FORFAIT_A}:
        return equipe_b_id
    if m.statut in {StatutMatch.FORFAIT_B}:
        return equipe_a_id
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
    return None  # égalité


def ordonner_classement_groupe(groupe) -> list[Classement]:
    """
    Retourne la liste des Classement du groupe, triée selon les tie-breaks :
    1) points_classement
    2) différence
    3) points marqués
    4) confrontation directe (2 équipes) ou mini-ligue (>=3)
    5) rang_manuel (admin)
    """
    rows = list(Classement.objects.filter(groupe=groupe).select_related("equipe"))
    if not rows:
        return []

    # Tri de base (1-2-3 + 5)
    rows.sort(
        key=lambda c: (
            -c.points_classement,
            -c.difference,
            -c.points_marques,
            _key_admin(c.rang_manuel),
            c.equipe.nom,
        )
    )

    # Regrouper les égalités sur (1,2,3)
    def bucket_key(c: Classement):
        return (c.points_classement, c.difference, c.points_marques)

    i = 0
    while i < len(rows):
        j = i + 1
        while j < len(rows) and bucket_key(rows[j]) == bucket_key(rows[i]):
            j += 1

        bloc = rows[i:j]
        if len(bloc) == 2:
            a, b = bloc[0], bloc[1]
            gagnant_id = _departager_par_confrontation_directe(groupe.id, a.equipe_id, b.equipe_id)
            if gagnant_id is not None:
                if gagnant_id == b.equipe_id:
                    rows[i], rows[i + 1] = rows[i + 1], rows[i]

        elif len(bloc) >= 3:
            ids = [c.equipe_id for c in bloc]
            stats = {eid: MiniStats() for eid in ids}
            for m in _matches_finalises_entre(groupe.id, ids):
                _appliquer_resultat_mini(stats, m)

            # tri du bloc via mini-ligue, puis admin
            bloc.sort(
                key=lambda c: (
                    -stats[c.equipe_id].points,
                    -stats[c.equipe_id].diff,
                    -stats[c.equipe_id].points_pour,
                    _key_admin(c.rang_manuel),
                    c.equipe.nom,
                )
            )
            rows[i:j] = bloc

        i = j

    return rows
