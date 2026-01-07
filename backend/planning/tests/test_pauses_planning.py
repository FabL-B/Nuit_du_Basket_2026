from datetime import date, datetime

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import Edition
from planning.models import Creneau, PausePlanning
from planning.services_pauses import recalculer_debuts_creneaux_avec_pauses


@pytest.mark.django_db
def test_pause_decale_les_creneaux_apres_debut_pause():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    # duree_creneau_minutes supposée présente depuis bloc 3.6 fix
    assert hasattr(edition, "duree_creneau_minutes")

    # 6 créneaux
    base = timezone.make_aware(datetime(2026, 6, 20, 14, 0))
    for i in range(1, 7):
        Creneau.objects.create(edition=edition, index=i, debut=base, duree_minutes=edition.duree_creneau_minutes)
        base = base + timezone.timedelta(minutes=edition.duree_creneau_minutes)

    # pause à 15:00 pendant 60 min => le créneau index 5 (15:00) doit passer à 16:00
    pause_start = timezone.make_aware(datetime(2026, 6, 20, 15, 0))
    PausePlanning.objects.create(edition=edition, nom="Concours shoot", debut=pause_start, duree_minutes=60)

    recalculer_debuts_creneaux_avec_pauses(edition)

    c1 = Creneau.objects.get(edition=edition, index=1)
    c4 = Creneau.objects.get(edition=edition, index=4)
    c5 = Creneau.objects.get(edition=edition, index=5)
    c6 = Creneau.objects.get(edition=edition, index=6)

    assert c1.debut == timezone.make_aware(datetime(2026, 6, 20, 14, 0))
    assert c4.debut == timezone.make_aware(datetime(2026, 6, 20, 14, 45))
    assert c5.debut == timezone.make_aware(datetime(2026, 6, 20, 16, 0))
    assert c6.debut == timezone.make_aware(datetime(2026, 6, 20, 16, 15))


@pytest.mark.django_db
def test_pause_doits_aligner_sur_duree_creneau():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))

    pause_bad = PausePlanning(
        edition=edition,
        nom="Mauvaise pause",
        debut=timezone.make_aware(datetime(2026, 6, 20, 15, 7)),  # pas multiple de 15
        duree_minutes=60,
    )

    with pytest.raises(ValidationError):
        pause_bad.full_clean()
