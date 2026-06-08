import pytest
from httpx import AsyncClient

async def setup_analytics_data(client, admin_headers):
    # Setup league
    l_res = await client.post("/api/leagues", json={"name": "Analytics League"}, headers=admin_headers)
    l_id = l_res.json()["id"]
    
    # Setup 2 Teams
    t1_res = await client.post("/api/teams", json={"name": "ATeam", "league_id": l_id}, headers=admin_headers)
    t2_res = await client.post("/api/teams", json={"name": "BTeam", "league_id": l_id}, headers=admin_headers)
    t1_id = t1_res.json()["id"]
    t2_id = t2_res.json()["id"]

    # Add 11 players to each
    for i in range(11):
        await client.post("/api/players", json={"first_name": "A", "last_name": f"P{i}", "number": i, "team_id": t1_id}, headers=admin_headers)
        await client.post("/api/players", json={"first_name": "B", "last_name": f"P{i}", "number": i, "team_id": t2_id}, headers=admin_headers)

    # Need the exact player ID of ATeam's striker
    players = await client.get("/api/players")
    striker_id = next(p["id"] for p in players.json() if p["team_id"] == t1_id and p["last_name"] == "P9")

    # Setup schedule and game
    s_res = await client.post("/api/schedules", json={"league_id": l_id, "name": "R1"}, headers=admin_headers)
    s_id = s_res.json()["id"]

    loc_res = await client.post("/api/locations", json={"name": "Loc A", "time_zone_id": "UTC"}, headers=admin_headers)
    loc_id = loc_res.json()["id"]

    g_res = await client.post("/api/games", json={
        "schedule_id": s_id, "home_team_id": t1_id, "visitor_team_id": t2_id, 
        "location_id": loc_id, "name": "M1"
    }, headers=admin_headers)
    game_id = g_res.json()["id"]

    # Add 3 goals for striker against BTeam
    for _ in range(3):
        await client.post("/api/goals", json={"game_id": game_id, "player_id": striker_id, "team_id": t1_id, "minute": 10}, headers=admin_headers)

    return t1_id, t2_id, striker_id

@pytest.mark.asyncio
async def test_get_best_player_vs_team(client: AsyncClient, admin_headers):
    # FT-07
    t1_id, t2_id, striker_id = await setup_analytics_data(client, admin_headers)

    res = await client.get(f"/api/stats/best-player-vs-team/{t2_id}")
    assert res.status_code == 200
    data = res.json()
    assert "player" in data
    assert data["player"]["id"] == striker_id
    assert data["goals"] == 3

@pytest.mark.asyncio
async def test_get_best_teams(client: AsyncClient, admin_headers):
    t1_id, t2_id, _ = await setup_analytics_data(client, admin_headers)
    
    # Needs to test the analytics endpoints 
    res = await client.get("/api/stats/teams")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

@pytest.mark.asyncio
async def test_get_best_players(client: AsyncClient, admin_headers):
    await setup_analytics_data(client, admin_headers)
    res = await client.get("/api/stats/players")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
