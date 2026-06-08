import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_users_unauthorized(client: AsyncClient):
    response = await client.get("/api/users")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_and_get_user(client: AsyncClient, admin_headers):
    # Tworzenie użytkownika
    new_user = {
        "username": "newcoach",
        "password": "password123",
        "role": "coach"
    }
    response = await client.post("/api/users", json=new_user, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newcoach"
    assert data["role"] == "coach"
    assert "hashed_password" not in data

    # Pobieranie listy użytkowników
    response = await client.get("/api/users", headers=admin_headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2 # admin + newcoach
    assert any(u["username"] == "newcoach" for u in users)

@pytest.mark.asyncio
async def test_create_duplicate_user(client: AsyncClient, admin_headers):
    new_user = {
        "username": "testuser",
        "password": "testpassword",
        "role": "user"
    }
    # Pierwsze utworzenie - sukces
    response = await client.post("/api/users", json=new_user, headers=admin_headers)
    assert response.status_code == 200

    # Drugie utworzenie - błąd 400 (Wektor FT-02)
    response2 = await client.post("/api/users", json=new_user, headers=admin_headers)
    assert response2.status_code == 400
    assert "Username already registered" in response2.json()["detail"]

@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, admin_headers):
    # Setup
    new_user = {"username": "todelete", "password": "pwd", "role": "user"}
    res = await client.post("/api/users", json=new_user, headers=admin_headers)
    user_id = res.json()["id"]

    # Delete
    del_res = await client.delete(f"/api/users/{user_id}", headers=admin_headers)
    assert del_res.status_code == 200

    # Get users, todelete should be missing
    get_res = await client.get("/api/users", headers=admin_headers)
    assert not any(u["id"] == user_id for u in get_res.json())
