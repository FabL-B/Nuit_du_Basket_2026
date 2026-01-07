from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.utils.dateparse import parse_date
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


def _age_a_date(date_naissance: date, date_reference: date) -> int:
    """
    Calcule l'âge (années) à une date de référence.
    """
    years = date_reference.year - date_naissance.year
    # si anniversaire pas encore passé dans l'année de référence
    if (date_reference.month, date_reference.day) < (date_naissance.month, date_naissance.day):
        years -= 1
    return years


def _verifier_age_rookie(equipe: Equipe) -> None:
    """
    Règle : en Rookie, chaque joueur doit avoir >= 15 ans à la date de l'édition.
    """
    if equipe.tournoi.code != "ROOKIE":
        return

    date_ref = equipe.edition.date_evenement
    if isinstance(date_ref, str):
        date_ref = parse_date(date_ref)
    if not isinstance(date_ref, date):
        raise ErreurValidationEquipe("Date d'évènement invalide pour calculer l'âge (Edition.date_evenement).")

    # Ici, on exige une date de naissance renseignée pour pouvoir valider.
    joueurs_sans_date = equipe.joueurs.filter(date_naissance__isnull=True)
    if joueurs_sans_date.exists():
        raise ErreurValidationEquipe(
            "En tournoi Rookie, la date de naissance est obligatoire pour valider l'équipe."
        )

    joueurs = equipe.joueurs.all()
    for joueur in joueurs:
        age = _age_a_date(joueur.date_naissance, date_ref)
        if age < 15:
            raise ErreurValidationEquipe(
                f"En tournoi Rookie, aucun joueur ne peut avoir moins de 15 ans. "
                f"Joueur concerné: {joueur.prenom} {joueur.nom} ({age} ans)."
            )


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

    _verifier_age_rookie(equipe)

    equipe.statut = StatutEquipe.VALIDEE
    equipe.full_clean()
    equipe.save(update_fields=["statut", "modifie_le"])
    return equipe
