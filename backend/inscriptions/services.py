from django.db import transaction

from inscriptions.models import Equipe, StatutEquipe


class ErreurValidationEquipe(ValueError):
    pass


def _bornes_joueurs_par_tournoi(code_tournoi: str) -> tuple[int, int]:
    """
    Retourne (min_joueurs, max_joueurs) selon le code tournoi.
    Règles validées :
    - Loisir : 3 à 5
    - Rookie : 3 à 4
    - Compétiteur : 3 à 4
    """
    if code_tournoi == "LOISIR":
        return 3, 5
    if code_tournoi in {"ROOKIE", "COMPETITEUR"}:
        return 3, 4
    raise ErreurValidationEquipe(f"Code tournoi inconnu: {code_tournoi}")


@transaction.atomic
def valider_equipe(equipe: Equipe) -> Equipe:
    """
    Passe une équipe de BROUILLON -> VALIDEE si elle respecte :
    - bornes min/max joueurs selon tournoi

    Note : le contrôle d'âge Rookie (>= 15 ans) est traité au bloc 1.8.
    """
    code_tournoi = equipe.tournoi.code
    min_joueurs, max_joueurs = _bornes_joueurs_par_tournoi(code_tournoi)

    nb_joueurs = equipe.joueurs.count()
    if nb_joueurs < min_joueurs or nb_joueurs > max_joueurs:
        raise ErreurValidationEquipe(
            f"Une équipe {code_tournoi} validée doit contenir {min_joueurs} à {max_joueurs} joueurs. "
            f"Actuellement: {nb_joueurs}."
        )

    equipe.statut = StatutEquipe.VALIDEE
    equipe.full_clean()
    equipe.save(update_fields=["statut", "modifie_le"])
    return equipe
