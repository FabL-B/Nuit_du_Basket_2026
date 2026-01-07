import pytest
from django.db import IntegrityError

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe


@pytest.mark.django_db
def test_unique_nom_equipe_par_edition():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)

    Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Les Aigles")

    with pytest.raises(IntegrityError):
        Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Les Aigles")


@pytest.mark.django_db
def test_meme_nom_possible_sur_deux_editions():
    edition1 = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    edition2 = Edition.objects.create(nom="NDB 2027", date_evenement="2027-06-19")

    tournoi1 = Tournoi.objects.create(edition=edition1, code=CodeTournoi.ROOKIE)
    tournoi2 = Tournoi.objects.create(edition=edition2, code=CodeTournoi.ROOKIE)

    Equipe.objects.create(edition=edition1, tournoi=tournoi1, nom="Les Aigles")
    Equipe.objects.create(edition=edition2, tournoi=tournoi2, nom="Les Aigles")  # OK
