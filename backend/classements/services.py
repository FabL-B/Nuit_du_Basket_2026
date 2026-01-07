from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from classements.models import Classement
from groupes.models import GroupeEquipe
from matchs.models import Match, StatutMatch, Score


class ErreurClassement(ValueError):
    pass


@dataclass
class StatsEquipe:
    joues: int = 0
    gagnes: int = 0
    perdus: int = 0
    egalites: int = 0
    points_marques: int = 0
    points_encaisses: int = 0
    points_classement: int = 0

    @property
    def difference(self) -> int:
        return self.points_marques - self.points_encaisses


def _appliquer_resultat(stats_a: StatsEquipe, stats_b: StatsEquipe, pa: int, pb: int) -> None:
    """
    Applique un match terminé avec score (égalité autorisée).
    Barème :
    - victoire = 3
    - égalité = 2
    - défaite = 1
    """
    stats_a.joues += 1
    stats_b.joues += 1

    stats_a.points_marques += pa
    stats_a.points_encaisses += pb
    stats_b.points_marques += pb
    stats_b.points_encaisses += pa

    if pa > pb:
        stats_a.gagnes += 1
        stats_b.perdus += 1
        stats_a.points_classement += 3
        stats_b.points_classement += 1
    elif pa < pb:
        stats_b.gagnes += 1
        stats_a.perdus += 1
        stats_b.points_classement += 3
        stats_a.points_classement += 1
    else:
        stats_a.egalites += 1
        stats_b.egalites += 1
        stats_a.points_classement += 2
        stats_b.points_classement += 2


def _appliquer_forfait(stats_forfait: StatsEquipe, stats_gagnant: StatsEquipe) -> None:
    """
    Forfait :
    - équipe forfait : 0 point classement
    - équipe gagnante : victoire (3 points)
    Points marqués/encaissés : non définis par tes règles (pas de score),
    donc on ne modifie pas points_marques/encaisses ici.
    """
    stats_forfait.joues += 1
    stats_gagnant.joues += 1

    stats_forfait.points_classement += 0
    stats_gagnant.points_classement += 3

    stats_forfait.perdus += 1
    stats_gagnant.gagnes += 1


@transaction.atomic
def recalculer_classements_pour_groupe(groupe) -> None:
    """
    Recalcule intégralement les classements du groupe à partir :
    - des équipes affectées au groupe
    - des matchs du groupe dont le résultat est final :
      * TERMINE avec score validé
      * FORFAIT_* / DOUBLE_FORFAIT
    """
    equipe_ids = list(
        GroupeEquipe.objects.filter(groupe=groupe).values_list("equipe_id", flat=True)
    )
    if not equipe_ids:
        return

    stats = {eid: StatsEquipe() for eid in equipe_ids}

    # Matchs terminés avec score validé (source de vérité)
    matchs_termines = (
        Match.objects.filter(
            groupe=groupe,
            statut=StatutMatch.TERMINE,
            score__valide_le__isnull=False,
        )
        .select_related("score")
        .order_by("id")
    )

    for m in matchs_termines:
        a = m.equipe_a_id
        b = m.equipe_b_id
        if a not in stats or b not in stats:
            continue

        score = m.score
        _appliquer_resultat(stats[a], stats[b], score.points_a, score.points_b)

    # Forfaits
    matchs_forfaits = Match.objects.filter(
        groupe=groupe,
        statut__in={StatutMatch.FORFAIT_A, StatutMatch.FORFAIT_B, StatutMatch.DOUBLE_FORFAIT},
    ).order_by("id")

    for m in matchs_forfaits:
        a = m.equipe_a_id
        b = m.equipe_b_id
        if a not in stats or b not in stats:
            continue

        if m.statut == StatutMatch.FORFAIT_A:
            _appliquer_forfait(stats_forfait=stats[a], stats_gagnant=stats[b])
        elif m.statut == StatutMatch.FORFAIT_B:
            _appliquer_forfait(stats_forfait=stats[b], stats_gagnant=stats[a])
        else:  # DOUBLE_FORFAIT
            stats[a].joues += 1
            stats[b].joues += 1

    # Remplacement complet : pas de risques d’incréments cumulés
    Classement.objects.filter(groupe=groupe).delete()

    to_create = []
    for eid, s in stats.items():
        to_create.append(
            Classement(
                groupe=groupe,
                equipe_id=eid,
                joues=s.joues,
                gagnes=s.gagnes,
                perdus=s.perdus,
                egalites=s.egalites,
                points_marques=s.points_marques,
                points_encaisses=s.points_encaisses,
                difference=s.difference,
                points_classement=s.points_classement,
            )
        )
    Classement.objects.bulk_create(to_create)
