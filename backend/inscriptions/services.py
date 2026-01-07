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


def _nb_equipes_validees_meme_tournoi(equipe: Equipe) -> int:
    return (
        Equipe.objects.filter(
            edition=equipe.edition,
            tournoi=equipe.tournoi,
            statut=StatutEquipe.VALIDEE,
        )
        .exclude(id=equipe.id)
        .count()
    )


def _valider_equipe_sans_regle_11(equipe: Equipe) -> Equipe:
    """
    Interne : applique toutes les règles de validation (bornes + âge rookie),
    mais ne bloque pas le passage 10->11. Utilisée uniquement par la validation par 2.
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

    nb_validees = _nb_equipes_validees_meme_tournoi(equipe)
    # Interdiction de créer un tournoi à 11 équipes validées
    if nb_validees == 10:
        raise ErreurValidationEquipe(
            "Inscription refusée : 11 équipes dans un tournoi n'est pas autorisé. "
            "Attends qu'une 12e équipe soit inscrite puis valide 2 équipes d'un coup."
        )

    equipe.statut = StatutEquipe.VALIDEE
    equipe.full_clean()
    equipe.save(update_fields=["statut", "modifie_le"])
    return equipe


@transaction.atomic
def valider_deux_equipes_pour_passer_a_12(equipe_1: Equipe, equipe_2: Equipe) -> tuple[Equipe, Equipe]:
    """
    Permet de passer de 10 -> 12 équipes validées sans état intermédiaire à 11.
    Préconditions :
    - mêmes edition + tournoi
    - les deux équipes sont en BROUILLON
    - il y a exactement 10 équipes déjà VALIDEE dans ce tournoi (en excluant ces 2 équipes)
    """
    if equipe_1.id == equipe_2.id:
        raise ErreurValidationEquipe("Impossible de valider deux fois la même équipe.")

    if equipe_1.edition_id != equipe_2.edition_id or equipe_1.tournoi_id != equipe_2.tournoi_id:
        raise ErreurValidationEquipe("Les deux équipes doivent appartenir au même tournoi et à la même édition.")

    if equipe_1.statut == StatutEquipe.VALIDEE or equipe_2.statut == StatutEquipe.VALIDEE:
        raise ErreurValidationEquipe("Les deux équipes doivent être en brouillon avant validation.")

    nb_validees = (
        Equipe.objects.filter(
            edition=equipe_1.edition,
            tournoi=equipe_1.tournoi,
            statut=StatutEquipe.VALIDEE,
        )
        .exclude(id__in=[equipe_1.id, equipe_2.id])
        .count()
    )

    if nb_validees != 10:
        raise ErreurValidationEquipe(
            f"Validation par 2 non applicable : il y a {nb_validees} équipes validées (attendu: 10)."
        )

    # On réutilise les validations existantes (min/max + âge rookie),
    # mais on doit bypass la règle "==10 refuse" pendant cette transaction.
    # Solution simple : validation interne sans seuil 11.
    _valider_equipe_sans_regle_11(equipe_1)
    _valider_equipe_sans_regle_11(equipe_2)

    return equipe_1, equipe_2
