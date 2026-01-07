import pytest
from datetime import date


from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, Joueur, StatutEquipe
from inscriptions.services import valider_equipe, ErreurValidationEquipe


@pytest.mark.django_db
@pytest.mark.parametrize(
    "code_tournoi, nb_joueurs, attendu_ok",
    [
        (CodeTournoi.LOISIR, 2, False),
        (CodeTournoi.LOISIR, 3, True),
        (CodeTournoi.LOISIR, 5, True),
        (CodeTournoi.LOISIR, 6, False),
        (CodeTournoi.ROOKIE, 2, False),
        (CodeTournoi.ROOKIE, 3, True),
        (CodeTournoi.ROOKIE, 4, True),
        (CodeTournoi.ROOKIE, 5, False),
        (CodeTournoi.COMPETITEUR, 2, False),
        (CodeTournoi.COMPETITEUR, 3, True),
        (CodeTournoi.COMPETITEUR, 4, True),
        (CodeTournoi.COMPETITEUR, 5, False),
    ],
)
def test_valider_equipe_bornes_par_tournoi(code_tournoi, nb_joueurs, attendu_ok):
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=code_tournoi)

    equipe = Equipe.objects.create(
        edition=edition,
        tournoi=tournoi,
        nom=f"Equipe {code_tournoi}",
        statut=StatutEquipe.BROUILLON,
    )

    for i in range(nb_joueurs):
        date_naissance = None
        if code_tournoi == CodeTournoi.ROOKIE:
            # garantit >= 15 ans au 20/06/2026
            date_naissance = date(2000, 1, 1)

        Joueur.objects.create(
            equipe=equipe, prenom=f"P{i}", nom="Test", date_naissance=date_naissance
        )

    if attendu_ok:
        equipe_validee = valider_equipe(equipe)
        assert equipe_validee.statut == StatutEquipe.VALIDEE
    else:
        with pytest.raises(ErreurValidationEquipe):
            valider_equipe(equipe)


@pytest.mark.django_db
def test_valider_equipe_ok_avec_4_joueurs():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    equipe = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Les Lynx")

    for i in range(4):
        Joueur.objects.create(equipe=equipe, prenom=f"P{i}", nom="Test")

    equipe = valider_equipe(equipe)
    assert equipe.statut == StatutEquipe.VALIDEE
