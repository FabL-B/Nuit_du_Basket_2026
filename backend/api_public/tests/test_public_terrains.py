import pytest
from rest_framework.test import APIClient
from core.models import Edition
from planning.models import Terrain

pytestmark = pytest.mark.django_db


def test_public_terrains_default_only_active():
    client = APIClient()
    ed = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    Terrain.objects.create(edition=ed, nom="T1", type_terrain="INTERIEUR", ordre=1, est_actif=True)
    Terrain.objects.create(edition=ed, nom="T2", type_terrain="INTERIEUR", ordre=2, est_actif=False)

    r = client.get(f"/api/public/terrains/?edition={ed.id}", format="json")
    assert r.status_code == 200
    noms = [x["nom"] for x in r.data]
    assert "T1" in noms
    assert "T2" not in noms


def test_public_terrains_actif_false_returns_all():
    client = APIClient()
    ed = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    Terrain.objects.create(edition=ed, nom="T1", type_terrain="INTERIEUR", ordre=1, est_actif=True)
    Terrain.objects.create(edition=ed, nom="T2", type_terrain="INTERIEUR", ordre=2, est_actif=False)

    r = client.get(f"/api/public/terrains/?edition={ed.id}&actif=0", format="json")
    assert r.status_code == 200
    noms = [x["nom"] for x in r.data]
    assert "T1" in noms
    assert "T2" in noms
