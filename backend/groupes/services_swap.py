from __future__ import annotations

from django.db import transaction

from groupes.models import GroupeEquipe


class ErreurSwapGroupes(ValueError):
    pass


@transaction.atomic
def swap_equipes_entre_groupes(
    groupe_equipe_a: GroupeEquipe, groupe_equipe_b: GroupeEquipe
) -> None:
    """
    Interchange deux affectations (équipe A dans groupe A) et (équipe B dans groupe B).

    Préconditions strictes :
    - les deux GroupeEquipe appartiennent à la même sous-phase
    - les deux équipes appartiennent au même tournoi et à la même édition (garanti par modèle, mais on revalide)
    - les deux entrées sont différentes
    """
    if groupe_equipe_a.id == groupe_equipe_b.id:
        raise ErreurSwapGroupes("Impossible d'interchanger la même affectation.")

    groupe_a = groupe_equipe_a.groupe
    groupe_b = groupe_equipe_b.groupe

    if groupe_a.sous_phase_id != groupe_b.sous_phase_id:
        raise ErreurSwapGroupes(
            "Interchange interdit : les groupes ne sont pas dans la même sous-phase."
        )

    equipe_a = groupe_equipe_a.equipe
    equipe_b = groupe_equipe_b.equipe

    # Double sécurité cohérence tournoi / édition
    sous_phase = groupe_a.sous_phase
    edition_id = sous_phase.phase_globale.edition_id
    tournoi_id = sous_phase.tournoi_id

    if equipe_a.edition_id != edition_id or equipe_b.edition_id != edition_id:
        raise ErreurSwapGroupes("Interchange interdit : équipe(s) d'une autre édition.")
    if equipe_a.tournoi_id != tournoi_id or equipe_b.tournoi_id != tournoi_id:
        raise ErreurSwapGroupes("Interchange interdit : équipe(s) d'un autre tournoi.")

    # Swap : on échange les équipes entre les deux lignes
    # On utilise update_fields pour rester minimal.
    groupe_equipe_a.equipe_id, groupe_equipe_b.equipe_id = (
        groupe_equipe_b.equipe_id,
        groupe_equipe_a.equipe_id,
    )

    # full_clean() pour faire appliquer la validation modèle (règle tournoi/édition)
    groupe_equipe_a.full_clean()
    groupe_equipe_b.full_clean()

    groupe_equipe_a.save(update_fields=["equipe"])
    groupe_equipe_b.save(update_fields=["equipe"])
