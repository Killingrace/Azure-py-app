import pytest
from httpx import AsyncClient
import sqlalchemy as sa
from database import AsyncSessionLocal
import models

@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    # ST-02: Dostęp bez JWT
    endpoints = [
        ("GET", "/api/users"),
        ("POST", "/api/leagues"),
        ("POST", "/api/teams"),
        ("POST", "/api/players")
    ]
    for method, url in endpoints:
        res = await client.request(method, url)
        assert res.status_code == 401

@pytest.mark.asyncio
async def test_sql_injection_login(client: AsyncClient):
    # ST-03: Próba wstrzyknięcia SQL w pole username
    malicious_username = "admin' OR 1=1;--"
    response = await client.post(
        "/api/token", 
        data={"username": malicious_username, "password": "password"}
    )
    # Backend wykorzystuje ORM z parametryzacją zapytań, więc potraktuje to jako zwykły string
    # i nie zautoryzuje użytkownika (zwróci 401 Unauthorized)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_xss_data_storage(client: AsyncClient, admin_headers):
    # ST-04: Wprowadzenie skryptu XSS
    # Backend powinien przyjąć string jako dane (bez wykonywania) 
    # Ochrona odbywa się po stronie frontendu (React)
    l_res = await client.post("/api/leagues", json={"name": "XSS League"}, headers=admin_headers)
    l_id = l_res.json()["id"]

    malicious_payload = "<script>alert('XSS')</script>"
    t_res = await client.post("/api/teams", json={"name": malicious_payload, "league_id": l_id}, headers=admin_headers)
    
    assert t_res.status_code == 200
    assert t_res.json()["name"] == malicious_payload # String zachowany dokładnie w takiej samej postaci

@pytest.mark.asyncio
async def test_password_encryption_in_db():
    # ST-06: Weryfikacja sposobu przechowywania haseł (bcrypt)
    # Używamy bezpośrednio sesji bazy danych, by ominąć maskowanie (schemas.UserResponse ucina hasło)
    async with AsyncSessionLocal() as db:
        result = await db.execute(sa.select(models.User).filter(models.User.username == "admin"))
        user = result.scalar_one_or_none()
        
        assert user is not None
        # Hasze bcrypt zaczynają się od $2b$ (lub $2a$, $2y$)
        assert user.hashed_password.startswith("$2b$")
        assert len(user.hashed_password) >= 60 # Hasze bcrypt mają z reguły 60 znaków
        assert user.hashed_password != "admin" # Hasło nie jest przechowywane jawnym tekstem

@pytest.mark.asyncio
async def test_data_integrity_delete_team_with_game(client: AsyncClient, admin_headers, db_session):
    # ST-05: Usunięcie drużyny posiadającej zaplanowany mecz
    
    # 1. Tworzymy ligę
    l_res = await client.post("/api/leagues", json={"name": "Integrity League"}, headers=admin_headers)
    l_id = l_res.json()["id"]

    # 2. Tworzymy drużynę A i B
    t1_res = await client.post("/api/teams", json={"name": "Int Team A", "league_id": l_id}, headers=admin_headers)
    t1_id = t1_res.json()["id"]
    t2_res = await client.post("/api/teams", json={"name": "Int Team B", "league_id": l_id}, headers=admin_headers)
    t2_id = t2_res.json()["id"]

    # 3. Tworzymy harmonogram i lokalizację
    s_res = await client.post("/api/schedules", json={"league_id": l_id, "name": "Round 1"}, headers=admin_headers)
    s_id = s_res.json()["id"]
    loc_res = await client.post("/api/locations", json={"name": "Stadium", "time_zone_id": "UTC"}, headers=admin_headers)
    loc_id = loc_res.json()["id"]

    # 4. Tworzymy mecz (łączy t1 i t2)
    game_data = {
        "schedule_id": s_id,
        "home_team_id": t1_id,
        "visitor_team_id": t2_id,
        "location_id": loc_id,
        "name": "Match 1"
    }
    # Uwaga: w backendzie stworzenie meczu wymaga 11 graczy (zgodnie z biznesową logiką)
    # Dodajemy graczy "na skróty"
    for i in range(11):
        await client.post("/api/players", json={"first_name": "A", "last_name": f"P{i}", "number": i, "team_id": t1_id}, headers=admin_headers)
        await client.post("/api/players", json={"first_name": "B", "last_name": f"P{i}", "number": i, "team_id": t2_id}, headers=admin_headers)

    g_res = await client.post("/api/games", json=game_data, headers=admin_headers)
    assert g_res.status_code == 200

    # Włączamy wymuszanie kluczy obcych dla SQLite (w Postgre jest to domyślne)
    await db_session.execute(sa.text("PRAGMA foreign_keys = ON"))

    # 5. Próbujemy usunąć drużynę biorącą udział w meczu
    del_res = await client.delete(f"/api/teams/{t1_id}", headers=admin_headers)
    
    # Baza zwróci IntegrityError ze względu na klucz obcy home_team_id w tabeli games.
    # W `crud.py` jest to przechwytywane i zwracane jako HTTP 400 Bad Request
    assert del_res.status_code == 400
    assert "Cannot delete" in del_res.json()["detail"] or "integrity" in str(del_res.json()["detail"]).lower()
