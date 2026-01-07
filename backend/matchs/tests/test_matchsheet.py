from datetime import date
import pytest

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe
from matchs.models import Match, MatchSheet


@pytest.mark.django_db
def test_cree_feuille_automatique_a_creation_match():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sous_phase = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )
    groupe = Groupe.objects.create(sous_phase=sous_phase, code="A")

    e1 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE
    )
    e2 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE
    )

    match = Match.objects.create(
        edition=edition,
        phase_globale=phase,
        sous_phase=sous_phase,
        groupe=groupe,
        equipe_a=e1,
        equipe_b=e2,
    )

    feuille = MatchSheet.objects.get(match=match)
    assert feuille.sheet_code is not None
    assert len(feuille.sheet_code) == 36


@pytest.mark.django_db
def test_sheet_code_unique():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    phase = PhaseGlobale.objects.create(
        edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1
    )
    sous_phase = SousPhase.objects.create(
        phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE
    )
    groupe = Groupe.objects.create(sous_phase=sous_phase, code="A")

    e1 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE
    )
    e2 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE
    )
    e3 = Equipe.objects.create(
        edition=edition, tournoi=tournoi, nom="E3", statut=StatutEquipe.VALIDEE
    )

    m1 = Match.objects.create(
        edition=edition,
        phase_globale=phase,
        sous_phase=sous_phase,
        groupe=groupe,
        equipe_a=e1,
        equipe_b=e2,
    )
    m2 = Match.objects.create(
        edition=edition,
        phase_globale=phase,
        sous_phase=sous_phase,
        groupe=groupe,
        equipe_a=e1,
        equipe_b=e3,
    )

    f1 = MatchSheet.objects.get(match=m1)
    f2 = MatchSheet.objects.get(match=m2)

    assert f1.sheet_code != f2.sheet_code
