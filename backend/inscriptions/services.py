from django.db import transaction

from inscriptions.models import Equipe, StatutEquipe


class ErreurValidationEquipe(ValueError):
    pass


@transaction.atomic
def valider_equipe(equipe: Equipe) -> Equipe:
    """
    Passe une équipe de BROUILLON -> VALIDEE si elle respecte:
    - 4 à 5 joueurs
    """
    nb_joueurs = equipe.joueurs.count()

    if nb_joueurs < 4 or nb_joueurs > 5:
        raise ErreurValidationEquipe(
            f"Une équipe validée doit contenir 4 à 5 joueurs. Actuellement: {nb_joueurs}."
        )

    equipe.statut = StatutEquipe.VALIDEE
    equipe.full_clean()  # vérifie notamment cohérence édition/tournoi
    equipe.save(update_fields=["statut", "modifie_le"])
    return equipe
