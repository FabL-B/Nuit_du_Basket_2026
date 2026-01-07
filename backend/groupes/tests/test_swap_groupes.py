from datetime import date

import pytest

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from phases.models import PhaseGlobale, SousPhase, TypePhaseGlobale, BrancheSousPhase
from inscriptions.models import Equipe, StatutEquipe
from groupes.models import Groupe, GroupeEquipe
from groupes.services_swap import swap_equipes_entre_groupes, ErreurSwapGroupes


def _setup():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    tournoi = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)
    phase = PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sous_phase = SousPhase.objects.create(phase_globale=phase, tournoi=tournoi, branche=BrancheSousPhase.AUCUNE)

    g1 = Groupe.objects.create(sous_phase=sous_phase, code="A")
    g2 = Groupe.objects.create(sous_phase=sous_phase, code="B")

    e1 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=tournoi, nom="E2", statut=StatutEquipe.VALIDEE)

    ge1 = GroupeEquipe.objects.create(groupe=g1, equipe=e1)
    ge2 = GroupeEquipe.objects.create(groupe=g2, equipe=e2)

    return sous_phase, g1, g2, e1, e2, ge1, ge2


@pytest.mark.django_db
def test_swap_ok():
    _, g1, g2, e1, e2, ge1, ge2 = _setup()

    swap_equipes_entre_groupes(ge1, ge2)

    ge1.refresh_from_db()
    ge2.refresh_from_db()

    assert ge1.groupe_id == g1.id
    assert ge2.groupe_id == g2.id
    assert ge1.equipe_id == e2.id
    assert ge2.equipe_id == e1.id


@pytest.mark.django_db
def test_swap_refuse_si_pas_meme_sous_phase():
    _, g1, _, e1, _, ge1, _ = _setup()

    # autre sous-phase
    edition2 = Edition.objects.create(nom="NDB 2027", date_evenement=date(2027, 6, 19))
    tournoi2 = Tournoi.objects.create(edition=edition2, code=CodeTournoi.LOISIR)
    phase2 = PhaseGlobale.objects.create(edition=edition2, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)
    sous_phase2 = SousPhase.objects.create(phase_globale=phase2, tournoi=tournoi2, branche=BrancheSousPhase.AUCUNE)

    g_other = Groupe.objects.create(sous_phase=sous_phase2, code="A")
    e_other = Equipe.objects.create(edition=edition2, tournoi=tournoi2, nom="EOTHER", statut=StatutEquipe.VALIDEE)
    ge_other = GroupeEquipe.objects.create(groupe=g_other, equipe=e_other)

    with pytest.raises(ErreurSwapGroupes):
        swap_equipes_entre_groupes(ge1, ge_other)


@pytest.mark.django_db
def test_swap_refuse_si_meme_affectation():
    _, _, _, _, _, ge1, _ = _setup()

    with pytest.raises(ErreurSwapGroupes):
        swap_equipes_entre_groupes(ge1, ge1)
