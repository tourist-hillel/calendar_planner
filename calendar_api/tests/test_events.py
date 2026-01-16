import pytest
from rest_framework import status
from django.urls import reverse
from calendar_api.factories import UserFactory, EventFactory, CategoryFactory
from events.models import Event
from datetime import timedelta, timezone


pytestmark = pytest.mark.django_db

@pytest.fixture
def auth_client(client):
    user = UserFactory()
    client.force_login(user=user)
    return client, user

class TestEventViewset:
    def test_list_events(self, auth_client):
        client, user = auth_client
        EventFactory.create_batch(4, user=user)
        EventFactory.create_batch(3)
        response = client.get(reverse('events-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 4

    