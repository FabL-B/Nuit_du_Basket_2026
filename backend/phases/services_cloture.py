from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from classements.models import Classement
from classements.services import recalculer_classements_pour_groupe
from groupes.models import Groupe
from matchs.models import Match, StatutMatch
from phases.models import PhaseGlobale, SousPhase, StatutPhase


class ErreurCloturePhase(ValueError):
    pass


@dataclass(frozen=True)
class ResumeCloturePhase:
    groupes: int
    matchs_total: int


def _match_est_finalise(statut: str) -> bool:
    return statut in {
        StatutMatch.TERMINE,
        StatutMatch.FORFAIT_A,
        StatutMatch.FORFAIT_B,
        StatutMatch.DOUBLE_FORFAIT,
    }


def _detecter_egalites_3_plus(classements: list[Classement]) -> list[list[Classement]]:
    """
    Retourne les "blocs" d'égalité de taille >= 3 sur (points, diff, points_marques).
    """
    # Tri stable pour regrouper
    classements = sorted(
        classements,
        key=lambda c: (c.points_classement, c.difference, c.points_marques),
        reverse=True,
    )

    blocs = []
    i = 0
    while i < len(classements):
        j = i + 1
        while (
            j < len(classements)
            and classements[j].points_classement == classements[i].points_classement
            and classements[j].difference == classements[i].difference
            and classements[j].points_marques == classements[i].points_marques
        ):
            j += 1

        bloc = classements[i:j]
        if len(bloc) >= 3:
            blocs.append(bloc)

        i = j

    return blocs


@transaction.atomic
def cloturer_phase_globale(phase_globale: PhaseGlobale) -> ResumeCloturePhase:
    """
    Clôture une PhaseGlobale + toutes ses SousPhase.

    Conditions:
    - tous les matchs de la phase sont finalisés (TERMINE ou forfaits)
    - si égalité >=3 équipes dans un groupe => rang_manuel obligatoire
    """
    # 1) Vérifier que tous les matchs sont finalisés
    matchs = list(Match.objects.filter(phase_globale=phase_globale).only("id", "statut", "groupe_id"))
    if not matchs:
        raise ErreurCloturePhase("Impossible de clôturer : aucun match pour cette phase globale.")

    non_finalises = [m.id for m in matchs if not _match_est_finalise(m.statut)]
    if non_finalises:
        raise ErreurCloturePhase(
            f"Impossible de clôturer : {len(non_finalises)} match(s) non finalisé(s) dans la phase globale."
        )

    # 2) Pour chaque groupe de la phase globale :
    #    - recalcul classement (sécurise la cohérence)
    #    - détecter égalités >=3 -> exiger rang_manuel
    groupes = list(
        Groupe.objects.filter(sous_phase__phase_globale=phase_globale)
        .select_related("sous_phase")
        .order_by("id")
    )
    if not groupes:
        raise ErreurCloturePhase("Impossible de clôturer : aucun groupe pour cette phase globale.")

    for g in groupes:
        recalculer_classements_pour_groupe(g)

        rows = list(Classement.objects.filter(groupe=g).select_related("equipe"))
        blocs = _detecter_egalites_3_plus(rows)

        for bloc in blocs:
            # règle process validée : rang_manuel obligatoire si égalité >=3
            if any(c.rang_manuel is None for c in bloc):
                noms = ", ".join(c.equipe.nom for c in bloc)
                raise ErreurCloturePhase(
                    f"Départage manuel requis (rang_manuel) pour le groupe {g.code} : {noms}"
                )

    # 3) Marquer la phase et les sous-phases comme clôturées
    phase_globale.statut = StatutPhase.CLOTUREE
    phase_globale.save(update_fields=["statut", "modifie_le"])

    SousPhase.objects.filter(phase_globale=phase_globale).update(statut=StatutPhase.CLOTUREE)
    
    return ResumeCloturePhase(groupes=len(groupes), matchs_total=len(matchs))
