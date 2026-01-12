import pytest

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, TypePhaseGlobale, BrancheSousPhase
from phases.services.sous_phases import (
    generer_sous_phases_pour_phase_globale,
    ErreurGenerationSousPhases,
)
from phases.services._shared import ErreurReglesPhase, verifier_edition_a_3_tournois


@pytest.mark.django_db
def test_generation_sous_phases_phase_1_cree_3():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.COMPETITEUR)

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )

    sous_phases = generer_sous_phases_pour_phase_globale(phase)
    assert len(sous_phases) == 3
    assert {sp.branche for sp in sous_phases} == {BrancheSousPhase.AUCUNE}


@pytest.mark.django_db
def test_generation_sous_phases_phase_2_cree_6():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.COMPETITEUR)

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_2, sequence=1
    )

    sous_phases = generer_sous_phases_pour_phase_globale(phase)
    assert len(sous_phases) == 6
    assert {sp.branche for sp in sous_phases} == {
        BrancheSousPhase.CHALLENGE,
        BrancheSousPhase.CONSOLANTE,
    }


@pytest.mark.django_db
def test_refuse_regeneration_si_deja_existant():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.COMPETITEUR)

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    generer_sous_phases_pour_phase_globale(phase)

    with pytest.raises(ErreurGenerationSousPhases):
        generer_sous_phases_pour_phase_globale(phase)


@pytest.mark.django_db
def test_refuse_si_tournois_incomplets():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)  # manque LOISIR + COMPETITEUR

    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )

    with pytest.raises(ErreurReglesPhase):
        verifier_edition_a_3_tournois(phase)
