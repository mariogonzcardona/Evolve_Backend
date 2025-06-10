
import pytest
from rest_framework.test import APIClient
from apps.users.models import CustomUser

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_users(db):
    admin = CustomUser.objects.create_user(
        email='admin@example.com',
        password='adminpass',
        nombre='Admin',
        apellido='Test',
        fecha_nacimiento='1990-01-01',
        genero='M',
        peso=80,
        estatura=1.80,
        padecimientos_medicos='Ninguno',
        telefono_personal='1111111111',
        telefono_emergencia='9999999999',
        role='admin',
        is_staff=True
    )
    coach = CustomUser.objects.create_user(
        email='coach@example.com',
        password='coachpass',
        nombre='Coach',
        apellido='Test',
        fecha_nacimiento='1990-01-01',
        genero='M',
        peso=75,
        estatura=1.75,
        padecimientos_medicos='Ninguno',
        telefono_personal='2222222222',
        telefono_emergencia='8888888888',
        role='coach'
    )
    athlete = CustomUser.objects.create_user(
        email='athlete@example.com',
        password='athletepass',
        nombre='Athlete',
        apellido='Test',
        fecha_nacimiento='2000-01-01',
        genero='F',
        peso=60,
        estatura=1.65,
        padecimientos_medicos='Ninguno',
        telefono_personal='3333333333',
        telefono_emergencia='7777777777',
        role='athlete'
    )
    CustomUser.objects.create_user(
        email='athlete2@example.com',
        password='athletepass',
        nombre='Athlete2',
        apellido='Test',
        fecha_nacimiento='2010-01-01',
        genero='F',
        peso=40,
        estatura=1.50,
        padecimientos_medicos='Ninguno',
        telefono_personal='4444444444',
        telefono_emergencia='6666666666',
        role='athlete'
    )
    return admin, coach, athlete

@pytest.mark.django_db
def test_admin_can_filter_all_roles(api_client, create_users):
    admin, _, _ = create_users
    api_client.force_authenticate(user=admin)

    response = api_client.get("/api/v1/users/?role=coach")
    assert response.status_code == 200
    assert all(user['role'] == 'coach' for user in response.data)

    response = api_client.get("/api/v1/users/?role=admin")
    assert response.status_code == 200
    assert all(user['role'] == 'admin' for user in response.data)

@pytest.mark.django_db
def test_coach_can_only_see_athletes(api_client, create_users):
    _, coach, _ = create_users
    api_client.force_authenticate(user=coach)

    response = api_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert all(user['role'] == 'athlete' for user in response.data)

    response = api_client.get("/api/v1/users/?role=admin")
    assert response.status_code == 200
    assert all(user['role'] == 'athlete' for user in response.data)

@pytest.mark.django_db
def test_athlete_can_only_see_self(api_client, create_users):
    _, _, athlete = create_users
    api_client.force_authenticate(user=athlete)

    response = api_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['email'] == athlete.email
