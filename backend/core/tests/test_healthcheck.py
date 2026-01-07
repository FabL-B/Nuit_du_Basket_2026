from django.urls import reverse


def test_healthcheck(client):
    url = reverse("healthcheck")
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
