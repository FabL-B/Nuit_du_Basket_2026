import pytest
from datetime import date

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from matchs.models import Match, StatutMatch


@pytest.mark.django_db
def test_match_finale_peut_etre_cree_sans_groupe():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    finale = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.FINALE, sequence=1)
    sp = SousPhase.objects.create(phase_globale=finale, tournoi=tournoi, branche=BrancheSousPhase.CHALLENGE)

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)

    m = Match.objects.create(
        edition=edition,
        phase_globale=finale,
        sous_phase=sp,
        groupe=None,
        equipe_a=e1,
        equipe_b=e2,
        statut=StatutMatch.A_PLANIFIER,
    )

    assert m.groupe is None
