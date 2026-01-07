from datetime import date
import pytest

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, Joueur, StatutEquipe
from inscriptions.services import valider_equipe, ErreurValidationEquipe, valider_deux_equipes_pour_passer_a_12


@pytest.mark.django_db
def test_refuse_validation_11e_equipe():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    # 10 équipes déjà validées
    for i in range(10):
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"Validee {i}", statut=StatutEquipe.VALIDEE
        )

    # équipe candidate (brouillon) avec 3 joueurs (loisir min=3)
    candidate = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="Candidate", statut=StatutEquipe.BROUILLON
    )
    for i in range(3):
        Joueur.objects.create(equipe=candidate, prenom=f"P{i}", nom="Test")

    with pytest.raises(ErreurValidationEquipe):
        valider_equipe(candidate)



@pytest.mark.django_db
def test_valider_deux_equipes_pour_passer_a_12():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)

    # 10 équipes validées
    for i in range(10):
        Equipe.objects.create(
            edition=edition, tournoi=tournoi, nom=f"Validee {i}", statut=StatutEquipe.VALIDEE
        )

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.BROUILLON)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.BROUILLON)

    # Rookie : min=3 max=4 + date naissance obligatoire (>=15)
    for i in range(3):
        Joueur.objects.create(equipe=e1, prenom=f"A{i}", nom="Test", date_naissance=date(2000, 1, 1))
        Joueur.objects.create(equipe=e2, prenom=f"B{i}", nom="Test", date_naissance=date(2000, 1, 1))

    valider_deux_equipes_pour_passer_a_12(e1, e2)

    assert e1.statut == StatutEquipe.VALIDEE
    assert e2.statut == StatutEquipe.VALIDEE
    assert Equipe.objects.filter(edition=edition, tournoi=tournoi, statut=StatutEquipe.VALIDEE).count() == 12