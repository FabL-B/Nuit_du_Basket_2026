from datetime import date, time

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Edition


@pytest.mark.django_db
def test_admin_peut_lister_editions():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.get("/api/admin/editions/")
    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_non_admin_est_refuse():
    User = get_user_model()
    user = User.objects.create_user(username="user", password="pass", is_staff=False)

    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/admin/editions/")
    assert resp.status_code == 403
