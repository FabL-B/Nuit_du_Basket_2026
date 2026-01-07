from datetime import date
import pytest
from django.core.exceptions import ValidationError

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe
from matchs.models import Match


@pytest.mark.django_db
def test_match_refuse_equipes_identiques():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sous_phase = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sous_phase, code="A")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)

    with pytest.raises(ValidationError):
        Match.objects.create(
            edition=edition,
            phase_globale=phase,
            sous_phase=sous_phase,
            groupe=groupe,
            equipe_a=e1,
            equipe_b=e1,
        )


@pytest.mark.django_db
def test_match_refuse_si_equipe_pas_bon_tournoi():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi_loisir = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    tournoi_rookie = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)

    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sous_phase = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi_loisir, branche=BrancheSousPhase.AUCUNE)
    groupe = Groupe.objects.create(sous_phase=sous_phase, code="A")

    e_loisir = Equipe.objects.create(edition=edition, tournoi=tournoi_loisir, nom="E1", statut=StatutEquipe.VALIDEE)
    e_rookie = Equipe.objects.create(edition=edition, tournoi=tournoi_rookie, nom="E2", statut=StatutEquipe.VALIDEE)

    with pytest.raises(ValidationError):
        Match.objects.create(
            edition=edition,
            phase_globale=phase,
            sous_phase=sous_phase,
            groupe=groupe,
            equipe_a=e_loisir,
            equipe_b=e_rookie,
        )
