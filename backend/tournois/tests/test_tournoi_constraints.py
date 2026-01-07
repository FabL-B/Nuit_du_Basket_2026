import pytest
from django.db import IntegrityError
from core.models import Edition
from tournois.models import Tournoi, CodeTournoi


@pytest.mark.django_db
def test_unique_tournoi_par_edition_et_code():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)

    with pytest.raises(IntegrityError):
        Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
