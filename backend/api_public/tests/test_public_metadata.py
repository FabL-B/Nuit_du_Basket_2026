import pytest
from rest_framework.test import APIClient

from core.models import Edition
from planning.models import Terrain

pytestmark = pytest.mark.django_db


def test_public_editions_list():
    Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    client = APIClient()

    r = client.get("/api/public/editions/", format="json")
    assert r.status_code == 200
    assert len(r.data) >= 1
    assert "date_evenement" in r.data[0]


def test_public_terrains_list_defaults_to_active_only():
    edition = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")
    Terrain.objects.create(edition=edition, nom="T1", ordre=1, est_actif=True)
    Terrain.objects.create(edition=edition, nom="T2", ordre=2, est_actif=False)

    client = APIClient()
    r = client.get("/api/public/terrains/?edition=%s" % edition.id, format="json")
    assert r.status_code == 200
    assert len(r.data) == 1
    assert r.data[0]["nom"] == "T1"
