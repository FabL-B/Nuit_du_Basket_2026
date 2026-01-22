import pytest
from rest_framework.test import APIClient
from core.models import Edition

pytestmark = pytest.mark.django_db


def test_public_editions_active_returns_last():
    client = APIClient()
    Edition.objects.create(nom="NDB 2025", date_evenement="2025-06-20")
    last = Edition.objects.create(nom="NDB 2026", date_evenement="2026-06-20")

    r = client.get("/api/public/editions/active/", format="json")
    assert r.status_code == 200
    assert r.data["id"] == last.id
