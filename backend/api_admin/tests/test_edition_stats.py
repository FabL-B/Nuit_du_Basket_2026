import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, Joueur, StatutEquipe

pytestmark = pytest.mark.django_db


def mk_admin():
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )


def test_edition_stats_ok_and_group_by_categorie():
    admin = mk_admin()
    client = APIClient()
    client.force_authenticate(admin)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    t1 = Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    t2 = Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    e1 = Equipe.objects.create(edition=edition, tournoi=t1, nom="E1", statut=StatutEquipe.VALIDEE)
    e2 = Equipe.objects.create(edition=edition, tournoi=t2, nom="E2", statut=StatutEquipe.VALIDEE)
    Joueur.objects.create(equipe=e1, prenom="A", nom="A")
    Joueur.objects.create(equipe=e2, prenom="B", nom="B")

    r = client.get(f"/api/admin/editions/{edition.id}/stats/", format="json")
    assert r.status_code == 200, r.data
    assert r.data["equipes"] == 2
    assert r.data["joueurs"] == 2

    r2 = client.get(f"/api/admin/editions/{edition.id}/stats/?group_by=categorie", format="json")
    assert r2.status_code == 200, r2.data
    assert r2.data["group_by"] == "categorie"
    assert len(r2.data["rows"]) == 2
