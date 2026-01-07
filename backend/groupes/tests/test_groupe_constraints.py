import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe
from groupes.models import Groupe, GroupeEquipe


@pytest.mark.django_db
def test_unique_code_groupe_par_sous_phase():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sous_phase = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )

    Groupe.objects.create(sous_phase=sous_phase, code="A")

    with pytest.raises(IntegrityError):
        Groupe.objects.create(sous_phase=sous_phase, code="A")


@pytest.mark.django_db
def test_groupe_equipe_refuse_mauvais_tournoi():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi_rookie = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    tournoi_loisir = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sous_phase_rookie = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi_rookie, branche=BrancheSousPhase.AUCUNE
    )

    groupe = Groupe.objects.create(sous_phase=sous_phase_rookie, code="A")
    equipe_loisir = Equipe.objects.create(edition=edition, tournoi=tournoi_loisir, nom="Les Loups")

    with pytest.raises(ValidationError):
        GroupeEquipe.objects.create(groupe=groupe, equipe=equipe_loisir)


@pytest.mark.django_db
def test_groupe_equipe_refuse_mauvaise_edition():
    edition_2026 = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    edition_2027 = Edition.objects.create(nom="NDB 2027", date_evenement="2027-06-19")

    tournoi_2026 = Tournoi.objects.create(edition=edition_2026, code=CodeTournoi.ROOKIE)
    tournoi_2027 = Tournoi.objects.create(edition=edition_2027, code=CodeTournoi.ROOKIE)

    phase_2026 = PhaseGlobale.objects.create(
        edition=edition_2026, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sous_phase_2026 = SousPhase.objects.create(
        phase_globale=phase_2026, tournoi=tournoi_2026, branche=BrancheSousPhase.AUCUNE
    )

    groupe = Groupe.objects.create(sous_phase=sous_phase_2026, code="A")
    equipe_2027 = Equipe.objects.create(edition=edition_2027, tournoi=tournoi_2027, nom="Les Lynx")

    with pytest.raises(ValidationError):
        GroupeEquipe.objects.create(groupe=groupe, equipe=equipe_2027)


@pytest.mark.django_db
def test_groupe_equipe_ok():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sous_phase = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )

    groupe = Groupe.objects.create(sous_phase=sous_phase, code="A")
    equipe = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="Les Tigres")

    ge = GroupeEquipe.objects.create(groupe=groupe, equipe=equipe, seed=1)
    assert ge.id is not None
