from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Edition
from phases.models import PhaseGlobale, TypePhaseGlobale


@pytest.mark.django_db
def test_admin_peut_lister_phases_globales():
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="pass", is_staff=True)

    edition = Edition.objects.create(nom="NDB 2026", date_evenement=date(2026, 6, 20))
    PhaseGlobale.objects.create(edition=edition, type_phase=TypePhaseGlobale.PHASE_1, sequence=1)

    client = APIClient()
    client.force_authenticate(user=admin)

    resp = client.get("/api/admin/phases-globales/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_non_admin_refuse_phases_globales():
    User = get_user_model()
    user = User.objects.create_user(username="user", password="pass", is_staff=False)

    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/admin/phases-globales/")
    assert resp.status_code == 403
