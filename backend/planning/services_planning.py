from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from matchs.models import Match, StatutMatch
from phases.models import PhaseGlobale
from planning.models import Creneau, Terrain, TypeTerrain


class ErreurGenerationPlanning(ValueError):
    pass


@dataclass(frozen=True)
class ResumePlanning:
    matchs_planifies: int
    creneaux_utilises: int


def _datetime_debut_edition(phase_globale: PhaseGlobale) -> datetime:
    """
    Construit le datetime de début à partir de la date de l'édition + start_time.
    """
    edition = phase_globale.edition
    # edition.date_evenement est un DateField
    start_dt = datetime.combine(edition.date_evenement, edition.heure_debut)
    # timezone aware
    return timezone.make_aware(start_dt)


def _get_or_create_creneaux(phase_globale: PhaseGlobale, nb_minimum: int) -> list[Creneau]:
    """
    Garantit qu'il existe au moins nb_minimum créneaux pour l'édition.
    Crée les créneaux manquants à partir de l'heure de début édition.
    """
    edition = phase_globale.edition
    slot_minutes = edition.duree_creneau_minutes

    existants = list(Creneau.objects.filter(edition=edition).order_by("index"))
    if len(existants) >= nb_minimum:
        return existants

    start_dt = _datetime_debut_edition(phase_globale)

    # index commence à 1 (plus lisible)
    next_index = existants[-1].index + 1 if existants else 1
    next_start = existants[-1].debut + timedelta(minutes=existants[-1].duree_minutes) if existants else start_dt

    a_creer = []
    while len(existants) + len(a_creer) < nb_minimum:
        a_creer.append(
            Creneau(
                edition=edition,
                index=next_index,
                debut=next_start,
                duree_minutes=slot_minutes,
            )
        )
        next_index += 1
        next_start = next_start + timedelta(minutes=slot_minutes)

    Creneau.objects.bulk_create(a_creer)
    return list(Creneau.objects.filter(edition=edition).order_by("index"))


def _penalite_match(
    match: Match,
    slot_index: int,
    type_terrain: str,
    last_slot_played: dict[int, int | None],
    counts_in: dict[int, int],
    counts_out: dict[int, int],
) -> int:
    """
    Score de pénalité (plus bas = meilleur).
    Contraintes souples :
    - éviter match sur 2 créneaux consécutifs
    - équilibrage intérieur/extérieur
    """
    a = match.equipe_a_id
    b = match.equipe_b_id

    pen = 0

    # Éviter 2 créneaux consécutifs
    for tid in (a, b):
        last = last_slot_played.get(tid)
        if last is None:
            continue
        if last == slot_index - 1:
            pen += 50  # gros malus
        elif last == slot_index - 2:
            pen += 10  # petit malus (ça commence à enchaîner)

    # Équilibrage intérieur/extérieur (souple)
    for tid in (a, b):
        in_cnt = counts_in.get(tid, 0)
        out_cnt = counts_out.get(tid, 0)
        diff = in_cnt - out_cnt  # positif => trop intérieur

        if type_terrain == TypeTerrain.INTERIEUR:
            # si déjà trop intérieur, malus
            if diff > 0:
                pen += 5 * diff
        else:
            # si déjà trop extérieur, malus
            if diff < 0:
                pen += 5 * (-diff)

    return pen


@transaction.atomic
def generer_planning_phase_globale(phase_globale: PhaseGlobale) -> ResumePlanning:
    """
    Planifie tous les matchs A_PLANIFIER d'une phase globale :
    - affecte creneau + terrain
    - passe statut à PLANIFIE
    - crée autant de créneaux que nécessaire

    Refuse si des matchs sont déjà planifiés (creneau/terrain non null) pour cette phase.
    """
    # Anti-regénération
    if Match.objects.filter(phase_globale=phase_globale).filter(creneau__isnull=False).exists():
        raise ErreurGenerationPlanning(
            "Des matchs sont déjà planifiés pour cette phase globale. Suppression/rollback manuel requis avant régénération."
        )

    terrains = list(
        Terrain.objects.filter(edition=phase_globale.edition, est_actif=True).order_by("ordre", "id")
    )
    if not terrains:
        raise ErreurGenerationPlanning("Aucun terrain actif pour cette édition.")
    nb_terrains = len(terrains)

    # Matchs à planifier : uniquement ceux sans créneau/terrain
    matchs = list(
        Match.objects.filter(phase_globale=phase_globale, statut=StatutMatch.A_PLANIFIER)
        .select_related("terrain", "creneau")
        .order_by("id")
    )
    if not matchs:
        return ResumePlanning(matchs_planifies=0, creneaux_utilises=0)

    # Minimum de créneaux requis si on remplissait toujours à nb_terrains
    nb_min_creneaux = (len(matchs) + nb_terrains - 1) // nb_terrains
    creneaux = _get_or_create_creneaux(phase_globale, nb_min_creneaux)

    # État de planification
    last_slot_played: dict[int, int | None] = {}
    counts_in: dict[int, int] = {}
    counts_out: dict[int, int] = {}

    restant = matchs[:]  # liste mutable

    # Itération sur créneaux, et si on n'arrive pas à tout placer, on crée des créneaux supplémentaires
    slot_ptr = 0
    while restant:
        if slot_ptr >= len(creneaux):
            # besoin d'un créneau de plus
            creneaux = _get_or_create_creneaux(phase_globale, len(creneaux) + 1)

        creneau = creneaux[slot_ptr]
        slot_index = creneau.index

        equipes_deja_prises: set[int] = set()
        terrains_utilises: set[int] = set()

        # Pour ce créneau, on tente de placer jusqu'à nb_terrains matchs
        placements = []

        for terrain in terrains:
            if not restant:
                break

            if terrain.id in terrains_utilises:
                continue

            # candidats = matchs dont aucune équipe ne joue déjà sur ce créneau
            candidats = [
                m for m in restant
                if (m.equipe_a_id not in equipes_deja_prises) and (m.equipe_b_id not in equipes_deja_prises)
            ]
            if not candidats:
                break

            # choisir le meilleur candidat selon pénalités souples
            candidats.sort(
                key=lambda m: _penalite_match(
                    m,
                    slot_index=slot_index,
                    type_terrain=terrain.type_terrain,
                    last_slot_played=last_slot_played,
                    counts_in=counts_in,
                    counts_out=counts_out,
                )
            )
            choisi = candidats[0]

            placements.append((choisi, terrain))
            terrains_utilises.add(terrain.id)
            equipes_deja_prises.add(choisi.equipe_a_id)
            equipes_deja_prises.add(choisi.equipe_b_id)

        # Appliquer placements
        for match, terrain in placements:
            match.creneau = creneau
            match.terrain = terrain
            match.statut = StatutMatch.PLANIFIE
            match.save(update_fields=["creneau", "terrain", "statut", "modifie_le"])

            # stats soft
            last_slot_played[match.equipe_a_id] = slot_index
            last_slot_played[match.equipe_b_id] = slot_index

            if terrain.type_terrain == TypeTerrain.INTERIEUR:
                counts_in[match.equipe_a_id] = counts_in.get(match.equipe_a_id, 0) + 1
                counts_in[match.equipe_b_id] = counts_in.get(match.equipe_b_id, 0) + 1
            else:
                counts_out[match.equipe_a_id] = counts_out.get(match.equipe_a_id, 0) + 1
                counts_out[match.equipe_b_id] = counts_out.get(match.equipe_b_id, 0) + 1

            restant.remove(match)

        slot_ptr += 1

    # Nombre de créneaux réellement utilisés = max index ayant au moins un match
    used_slots = (
        Match.objects.filter(phase_globale=phase_globale, creneau__isnull=False)
        .values_list("creneau__index", flat=True)
        .distinct()
        .count()
    )

    return ResumePlanning(matchs_planifies=len(matchs), creneaux_utilises=used_slots)
