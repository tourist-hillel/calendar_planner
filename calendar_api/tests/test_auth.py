import pytest
from rest_framework import status
from django.urls import reverse
from calendar_api.factories import UserFactory
from calendar_api.utils import create_access_token, create_refresh_token
import jwt
from django.conf import settings


pytestmark = pytest.mark.django_db

class TestLoginView:
    login_url = reverse('jwt_token')
    user_cell_phone = '1234567899'
    user_pwd = 'LoginPwd123'

    def test_login_success(self, client):
        user = UserFactory(cell_phone=self.user_cell_phone, password=self.user_pwd)
        response = client.post(self.login_url, {
            'cell_phone': self.user_cell_phone,
            'password': self.user_pwd
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

        payload = jwt.decode(response.data['access'], settings.SECRET_KEY, algorithms=['HS256'])
        assert payload['user_id'] == user.id
    
    def test_login_wrong_password(self, client):
        UserFactory(cell_phone=self.user_cell_phone, password=self.user_pwd)
        response = client.post(self.login_url, {
            'cell_phone': self.user_cell_phone,
            'password': 'wrong_password'
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['error'] == 'Неправильні креди'
    