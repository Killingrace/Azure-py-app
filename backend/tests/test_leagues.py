import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_leagues_empty(client: AsyncClient):
    response = await client.get("/api/leagues")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_league(client: AsyncClient, admin_headers):
    response = await client.post("/api/leagues", json={"name": "Premier League"}, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Premier League"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_league_unauthorized(client: AsyncClient, coach_headers):
    # ST-01: Coach trying to create a league
    response = await client.post("/api/leagues", json={"name": "La Liga"}, headers=coach_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_league(client: AsyncClient, admin_headers):
    res = await client.post("/api/leagues", json={"name": "Serie A"}, headers=admin_headers)
    league_id = res.json()["id"]

    res_update = await client.put(f"/api/leagues/{league_id}", json={"name": "Serie B"}, headers=admin_headers)
    assert res_update.status_code == 200
    assert res_update.json()["name"] == "Serie B"

@pytest.mark.asyncio
async def test_delete_league(client: AsyncClient, admin_headers):
    res = await client.post("/api/leagues", json={"name": "Ligue 1"}, headers=admin_headers)
    league_id = res.json()["id"]

    res_del = await client.delete(f"/api/leagues/{league_id}", headers=admin_headers)
    assert res_del.status_code == 200

    res_get = await client.get("/api/leagues")
    assert not any(l["id"] == league_id for l in res_get.json())
