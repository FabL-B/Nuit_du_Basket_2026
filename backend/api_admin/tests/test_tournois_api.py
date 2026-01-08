from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi


@pytest.mark.django_db
def test_admin_peut_lister_tournois():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    Tournoi.objects.create(edition=edition, code=CodeTournoi.ROOKIE)
    Tournoi.objects.create(edition=edition, code=CodeTournoi.LOISIR)

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.get("/api/admin/tournois/")
    assert resp.status_code == 200

    # pagination ou non
    data = resp.data["results"] if isinstance(resp.data, dict) and "results" in resp.data else resp.data
    assert len(data) == 2


@pytest.mark.django_db
def test_non_admin_refuse_tournois():
    User = get_user_model()
    user = User.objects.create_user(username="user", password="pass", is_staff=False)

    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/admin/tournois/")
    assert resp.status_code == 403
