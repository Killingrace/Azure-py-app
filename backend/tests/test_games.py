import pytest
from httpx import AsyncClient

async def setup_teams(client, admin_headers):
    l_res = await client.post("/api/leagues", json={"name": "GameLeague"}, headers=admin_headers)
    l_id = l_res.json()["id"]
    t1_res = await client.post("/api/teams", json={"name": "TeamA", "league_id": l_id}, headers=admin_headers)
    t2_res = await client.post("/api/teams", json={"name": "TeamB", "league_id": l_id}, headers=admin_headers)
    t1_id = t1_res.json()["id"]
    t2_id = t2_res.json()["id"]

    s_res = await client.post("/api/schedules", json={"league_id": l_id, "name": "Round 1"}, headers=admin_headers)
    s_id = s_res.json()["id"]

    loc_res = await client.post("/api/locations", json={"name": "Stadium A", "time_zone_id": "UTC"}, headers=admin_headers)
    loc_id = loc_res.json()["id"]

    return t1_id, t2_id, s_id, loc_id

@pytest.mark.asyncio
async def test_create_game_not_enough_players(client: AsyncClient, admin_headers):
    # FT-05
    t1_id, t2_id, s_id, loc_id = await setup_teams(client, admin_headers)
    
    # Try to create game without 11 players in each team
    game_data = {
        "schedule_id": s_id,
        "home_team_id": t1_id,
        "visitor_team_id": t2_id,
        "location_id": loc_id,
        "name": "Match 1"
    }
    res = await client.post("/api/games", json=game_data, headers=admin_headers)
    assert res.status_code == 400
    assert "does not have enough players (min 11)" in res.json()["detail"]

@pytest.mark.asyncio
async def test_create_game_success_and_score(client: AsyncClient, admin_headers, db_session):
    t1_id, t2_id, s_id, loc_id = await setup_teams(client, admin_headers)

    # Add 11 players to both teams
    for i in range(11):
        await client.post("/api/players", json={"first_name": "A", "last_name": f"P{i}", "number": i, "team_id": t1_id}, headers=admin_headers)
        await client.post("/api/players", json={"first_name": "B", "last_name": f"P{i}", "number": i, "team_id": t2_id}, headers=admin_headers)

    game_data = {
        "schedule_id": s_id,
        "home_team_id": t1_id,
        "visitor_team_id": t2_id,
        "location_id": loc_id,
        "name": "Match 1"
    }
    res = await client.post("/api/games", json=game_data, headers=admin_headers)
    assert res.status_code == 200
    game_id = res.json()["id"]

    # Set score
    score_res = await client.post(f"/api/games/{game_id}/score", json={"home_score": 2, "visitor_score": 1}, headers=admin_headers)
    assert score_res.status_code == 200
    assert score_res.json()["home_score"] == 2

    # FT-06: Coach from another team trying to set score
    from auth import create_access_token, get_password_hash
    import models
    coach_pwd = get_password_hash("pwd")
    db_session.add(models.User(username="hacker", hashed_password=coach_pwd, role="coach", team_id=999))
    await db_session.commit()
    
    unauth_coach_token = create_access_token(data={"sub": "hacker", "role": "coach", "team_id": 999})
    unauth_headers = {"Authorization": f"Bearer {unauth_coach_token}"}
    
    score_res_bad = await client.post(f"/api/games/{game_id}/score", json={"home_score": 9, "visitor_score": 9}, headers=unauth_headers)
    assert score_res_bad.status_code == 403
    assert "Not enough permissions" in score_res_bad.json()["detail"]
