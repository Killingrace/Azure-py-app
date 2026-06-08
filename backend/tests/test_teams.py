import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_team(client: AsyncClient, admin_headers):
    # Wektor FT-03
    # Utworzenie ligi
    league_res = await client.post("/api/leagues", json={"name": "Ekstraklasa"}, headers=admin_headers)
    league_id = league_res.json()["id"]

    # Utworzenie drużyny
    team_data = {"name": "Legia", "league_id": league_id}
    res = await client.post("/api/teams", json=team_data, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Legia"
    assert data["league_id"] == league_id

@pytest.mark.asyncio
async def test_update_team(client: AsyncClient, admin_headers):
    # Utworzenie ligi
    league_res = await client.post("/api/leagues", json={"name": "Bundesliga"}, headers=admin_headers)
    league_id = league_res.json()["id"]

    res = await client.post("/api/teams", json={"name": "Bayern", "league_id": league_id}, headers=admin_headers)
    team_id = res.json()["id"]

    update_res = await client.put(f"/api/teams/{team_id}", json={"name": "BVB", "league_id": league_id}, headers=admin_headers)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "BVB"

@pytest.mark.asyncio
async def test_delete_team(client: AsyncClient, admin_headers):
    # Utworzenie ligi
    league_res = await client.post("/api/leagues", json={"name": "Eredivisie"}, headers=admin_headers)
    league_id = league_res.json()["id"]

    res = await client.post("/api/teams", json={"name": "Ajax", "league_id": league_id}, headers=admin_headers)
    team_id = res.json()["id"]

    del_res = await client.delete(f"/api/teams/{team_id}", headers=admin_headers)
    assert del_res.status_code == 200

    get_res = await client.get("/api/teams")
    assert not any(t["id"] == team_id for t in get_res.json())
