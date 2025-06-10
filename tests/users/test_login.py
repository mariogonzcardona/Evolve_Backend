# import pytest
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth import get_user_model

# User = get_user_model()

# @pytest.fixture
# def api_client():
#     return APIClient()

# @pytest.fixture
# def test_password():
#     return 'testpass123'

# @pytest.fixture
# def test_user(test_password):
#     user_data = {
#         'username': 'testuser',
#         'password': test_password,
#         'email': 'test@example.com',
#         'first_name': 'Test',
#         'last_name': 'User',
#         'role': 'athlete'
#     }
#     user = User.objects.create_user(**user_data)
#     user.raw_password = test_password  # Guardamos la contraseña para las pruebas
#     return user

# @pytest.mark.django_db
# class TestUserLogin:
#     def test_login_successful(self, api_client, test_user, test_password):
#         """Test successful login with correct credentials"""
#         url = reverse('user-login')
#         response = api_client.post(url, {
#             'username': test_user.username,
#             'password': test_password
#         })
        
#         assert response.status_code == status.HTTP_200_OK
#         assert 'access' in response.data
#         assert 'refresh' in response.data
#         assert 'user' in response.data
        
#         # Verificar que los tokens sean válidos
#         refresh = RefreshToken(response.data['refresh'])
#         assert refresh['user_id'] == test_user.id

#     def test_login_wrong_password(self, api_client, test_user):
#         """Test login with incorrect password"""
#         url = reverse('user-login')
#         response = api_client.post(url, {
#             'username': test_user.username,
#             'password': 'wrongpassword'
#         })
        
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#         assert response.data['detail'] == 'Credenciales inválidas o cuenta inactiva.'

#     def test_login_inactive_user(self, api_client, test_user, test_password):
#         """Test login with inactive user"""
#         test_user.is_active = False
#         test_user.save()
        
#         url = reverse('user-login')
#         response = api_client.post(url, {
#             'username': test_user.username,
#             'password': test_password
#         })
        
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#         assert response.data['detail'] == 'Credenciales inválidas o cuenta inactiva.'

#     def test_login_missing_credentials(self, api_client):
#         """Test login with missing credentials"""
#         url = reverse('user-login')
#         response = api_client.post(url, {
#             'username': 'testuser'
#         })
        
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert 'password' in response.data

#     def test_login_invalid_username(self, api_client, test_password):
#         """Test login with non-existent username"""
#         url = reverse('user-login')
#         response = api_client.post(url, {
#             'username': 'nonexistentuser',
#             'password': test_password
#         })
        
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#         assert response.data['detail'] == 'Credenciales inválidas o cuenta inactiva.' 