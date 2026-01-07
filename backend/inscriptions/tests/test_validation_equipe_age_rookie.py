from datetime import date

import pytest

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, Joueur, StatutEquipe
from inscriptions.services import valider_equipe, ErreurValidationEquipe


@pytest.mark.django_db
def test_rookie_refuse_si_date_naissance_manquante():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    equipe = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Rookies", statut=StatutEquipe.BROUILLON)

    # 3 joueurs (min) mais sans date
    Joueur.objects.create(equipe=equipe, prenom="A", nom="Test", date_naissance=None)
    Joueur.objects.create(equipe=equipe, prenom="B", nom="Test", date_naissance=None)
    Joueur.objects.create(equipe=equipe, prenom="C", nom="Test", date_naissance=None)

    with pytest.raises(ErreurValidationEquipe):
        valider_equipe(equipe)


@pytest.mark.django_db
def test_rookie_refuse_si_joueur_moins_de_15_ans():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    equipe = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Rookies", statut=StatutEquipe.BROUILLON)

    # Un joueur né en 2012 => 14 ans au 20/06/2026 (anniversaire après le 20/06)
    Joueur.objects.create(equipe=equipe, prenom="A", nom="Test", date_naissance=date(2012, 7, 1))
    Joueur.objects.create(equipe=equipe, prenom="B", nom="Test", date_naissance=date(2010, 1, 1))
    Joueur.objects.create(equipe=equipe, prenom="C", nom="Test", date_naissance=date(2010, 1, 1))

    with pytest.raises(ErreurValidationEquipe):
        valider_equipe(equipe)


@pytest.mark.django_db
def test_rookie_ok_si_tous_les_joueurs_ont_15_ans_ou_plus():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    equipe = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Rookies", statut=StatutEquipe.BROUILLON)

    # 15 ans pile ou plus au 20/06/2026
    Joueur.objects.create(equipe=equipe, prenom="A", nom="Test", date_naissance=date(2011, 6, 20))  # 15 pile
    Joueur.objects.create(equipe=equipe, prenom="B", nom="Test", date_naissance=date(2010, 1, 1))
    Joueur.objects.create(equipe=equipe, prenom="C", nom="Test", date_naissance=date(2010, 1, 1))

    equipe_validee = valider_equipe(equipe)
    assert equipe_validee.statut == StatutEquipe.VALIDEE


@pytest.mark.django_db
def test_loisir_ne_verifie_pas_age():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    equipe = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Loisir", statut=StatutEquipe.BROUILLON)

    # 3 joueurs min, sans date de naissance => OK en loisir
    Joueur.objects.create(equipe=equipe, prenom="A", nom="Test", date_naissance=None)
    Joueur.objects.create(equipe=equipe, prenom="B", nom="Test", date_naissance=None)
    Joueur.objects.create(equipe=equipe, prenom="C", nom="Test", date_naissance=None)

    equipe_validee = valider_equipe(equipe)
    assert equipe_validee.statut == StatutEquipe.VALIDEE
