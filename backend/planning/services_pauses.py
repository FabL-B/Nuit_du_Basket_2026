from __future__ import annotations

from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from planning.models import Creneau, PausePlanning


class ErreurPausePlanning(ValueError):
    pass


def _debut_edition_aware(edition) -> datetime:
    dt = datetime.combine(edition.date_evenement, edition.heure_debut)
    return timezone.make_aware(dt)


def _charger_pauses_actives(edition) -> list[tuple[datetime, datetime]]:
    pauses = list(
        PausePlanning.objects.filter(edition=edition, est_active=True).order_by("debut")
    )
    intervals: list[tuple[datetime, datetime]] = []
    for p in pauses:
        intervals.append((p.debut, p.debut + timedelta(minutes=p.duree_minutes)))
    return intervals


def _sauter_si_dans_pause(dt: datetime, pauses: list[tuple[datetime, datetime]]) -> datetime:
    """
    Si dt est dans une pause (début inclus, fin exclue), on saute à la fin.
    Boucle pour gérer plusieurs pauses.
    """
    changed = True
    while changed:
        changed = False
        for start, end in pauses:
            if start <= dt < end:
                dt = end
                changed = True
                break
    return dt


@transaction.atomic
def recalculer_debuts_creneaux_avec_pauses(edition) -> None:
    """
    Recalcule *tous* les champs Creneau.debut à partir de :
    - la date + start_time de l'édition
    - la durée de créneau
    - les pauses actives
    Idempotent : tu peux relancer 10 fois, même résultat.
    """
    slot = getattr(edition, "duree_creneau_minutes", 15)
    pauses = _charger_pauses_actives(edition)

    creneaux = list(Creneau.objects.filter(edition=edition).order_by("index"))
    if not creneaux:
        return

    current = _debut_edition_aware(edition)

    for c in creneaux:
        current = _sauter_si_dans_pause(current, pauses)
        if c.debut != current:
            c.debut = current
            c.save(update_fields=["debut"])
        current = current + timedelta(minutes=slot)
