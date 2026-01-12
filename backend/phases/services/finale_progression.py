from django.db import transaction

from matchs.models import Match, StatutMatch, TourFinale
from phases.models import TypePhaseGlobale


class ErreurProgressionFinale(Exception):
    pass


_TOUR_SUIVANT = {
    TourFinale.HUITIEME: TourFinale.QUART,
    TourFinale.QUART: TourFinale.DEMI,
    TourFinale.DEMI: TourFinale.FINALE,
}


def _est_finalise(statut: str) -> bool:
    return statut in {
        StatutMatch.TERMINE,
        StatutMatch.FORFAIT_A,
        StatutMatch.FORFAIT_B,
        StatutMatch.DOUBLE_FORFAIT,
    }


def _get_vainqueur_finale(match: Match):
    if match.statut == StatutMatch.DOUBLE_FORFAIT:
        return None

    if match.statut == StatutMatch.FORFAIT_A:
        return match.equipe_b
    if match.statut == StatutMatch.FORFAIT_B:
        return match.equipe_a

    # TERMINE : score validé attendu
    if not hasattr(match, "score") or match.score.valide_le is None:
        return None

    if match.score.points_a > match.score.points_b:
        return match.equipe_a
    if match.score.points_b > match.score.points_a:
        return match.equipe_b

    return None


@transaction.atomic
def avancer_bracket_si_possible(match: Match) -> Match | None:
    """
    Si un match de phase finale est finalisé, tente de créer le match du tour suivant
    quand le match "frère" est aussi finalisé.
    Retourne le match créé (ou None si rien à faire).
    """
    match = Match.objects.select_related("phase_globale", "sous_phase").get(pk=match.pk)

    if match.phase_globale.type_phase != TypePhaseGlobale.FINALE:
        return None

    if not match.tour_finale or not match.numero_tour:
        raise ErreurProgressionFinale("Match finale sans tour_finale/numero_tour.")

    if not _est_finalise(match.statut):
        return None

    if match.tour_finale == TourFinale.FINALE:
        return None

    # match frère
    frere_num = match.numero_tour + 1 if match.numero_tour % 2 == 1 else match.numero_tour - 1
    frere = (
        Match.objects.filter(
            phase_globale=match.phase_globale,
            sous_phase=match.sous_phase,
            tour_finale=match.tour_finale,
            numero_tour=frere_num,
        )
        .select_related("score")
        .first()
    )

    if not frere or not _est_finalise(frere.statut):
        return None

    w_match = _get_vainqueur_finale(match)
    w_frere = _get_vainqueur_finale(frere)
    if not w_match or not w_frere:
        return None

    tour_suivant = _TOUR_SUIVANT[match.tour_finale]
    num_suivant = (min(match.numero_tour, frere.numero_tour) + 1) // 2  # 1&2 ->1 ; 3&4->2

    # idempotence : si déjà créé, ne rien faire
    nxt = Match.objects.filter(
        phase_globale=match.phase_globale,
        sous_phase=match.sous_phase,
        tour_finale=tour_suivant,
        numero_tour=num_suivant,
    ).first()
    if nxt:
        return None

    # ordre stable : vainqueur du plus petit numero_tour en equipe_a
    if match.numero_tour < frere.numero_tour:
        equipe_a, equipe_b = w_match, w_frere
    else:
        equipe_a, equipe_b = w_frere, w_match

    created = Match.objects.create(
        edition=match.edition,
        phase_globale=match.phase_globale,
        sous_phase=match.sous_phase,
        groupe=None,
        equipe_a=equipe_a,
        equipe_b=equipe_b,
        statut=StatutMatch.A_PLANIFIER,
        tour_finale=tour_suivant,
        numero_tour=num_suivant,
    )
    return created
