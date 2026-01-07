import pytest

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, Joueur, StatutEquipe
from inscriptions.services import valider_equipe, ErreurValidationEquipe


@pytest.mark.django_db
def test_valider_equipe_refuse_moins_de_4_joueurs():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    equipe = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Les Lynx")

    for i in range(3):
        Joueur.objects.create(equipe=equipe, prenom=f"P{i}", nom="Test")

    with pytest.raises(ErreurValidationEquipe):
        valider_equipe(equipe)


@pytest.mark.django_db
def test_valider_equipe_ok_avec_4_joueurs():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    equipe = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Les Lynx")

    for i in range(4):
        Joueur.objects.create(equipe=equipe, prenom=f"P{i}", nom="Test")

    equipe = valider_equipe(equipe)
    assert equipe.statut == StatutEquipe.VALIDEE
