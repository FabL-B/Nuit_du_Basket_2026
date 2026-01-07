import pytest
from django.db import IntegrityError
from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase


@pytest.mark.django_db
def test_unique_sous_phase_par_phase_globale_tournoi_branche():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)

    phase = PhaseGlobale.objects.create(
        edition=edition,
        type_phase=TypePhaseGlobale.PHASE_1,
        sequence=1,
    )

    SousPhase.objects.create(
        phase_globale=phase,
        tournoi=tournoi,
        branche=BrancheSousPhase.AUCUNE,
    )

    with pytest.raises(IntegrityError):
        SousPhase.objects.create(
            phase_globale=phase,
            tournoi=tournoi,
            branche=BrancheSousPhase.AUCUNE,
        )
