import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_player(client: AsyncClient, admin_headers):
    # Setup league and team
    l_res = await client.post("/api/leagues", json={"name": "L1"}, headers=admin_headers)
    t_res = await client.post("/api/teams", json={"name": "T1", "league_id": l_res.json()["id"]}, headers=admin_headers)
    team_id = t_res.json()["id"]

    player_data = {"first_name": "John", "last_name": "Doe", "number": 10, "team_id": team_id}
    p_res = await client.post("/api/players", json=player_data, headers=admin_headers)
    assert p_res.status_code == 200
    assert p_res.json()["first_name"] == "John"

@pytest.mark.asyncio
async def test_coach_create_player_for_own_team(client: AsyncClient, admin_headers, db_session):
    l_res = await client.post("/api/leagues", json={"name": "L2"}, headers=admin_headers)
    t_res = await client.post("/api/teams", json={"name": "T2", "league_id": l_res.json()["id"]}, headers=admin_headers)
    team_id = t_res.json()["id"]

    # Tworzymy trenera dla tej konkretnej drużyny w bazie i generujemy token
    from auth import create_access_token, get_password_hash
    import models
    coach_pwd = get_password_hash("pwd")
    db_session.add(models.User(username="coach_own", hashed_password=coach_pwd, role="coach", team_id=team_id))
    await db_session.commit()
    coach_token = create_access_token(data={"sub": "coach_own", "role": "coach", "team_id": team_id})
    
    player_data = {"first_name": "Jan", "last_name": "Kowalski", "number": 9, "team_id": team_id}
    p_res = await client.post("/api/players", json=player_data, headers={"Authorization": f"Bearer {coach_token}"})
    assert p_res.status_code == 200

@pytest.mark.asyncio
async def test_coach_create_player_for_other_team(client: AsyncClient, admin_headers, db_session):
    l_res = await client.post("/api/leagues", json={"name": "L3"}, headers=admin_headers)
    t_res = await client.post("/api/teams", json={"name": "T3", "league_id": l_res.json()["id"]}, headers=admin_headers)
    team_id = t_res.json()["id"]

    # Trener innej drużyny
    from auth import create_access_token, get_password_hash
    import models
    coach_pwd = get_password_hash("pwd")
    db_session.add(models.User(username="coach_other", hashed_password=coach_pwd, role="coach", team_id=999))
    await db_session.commit()
    coach_token = create_access_token(data={"sub": "coach_other", "role": "coach", "team_id": 999})

    player_data = {"first_name": "Jan", "last_name": "Nowak", "number": 8, "team_id": team_id}
    p_res = await client.post("/api/players", json=player_data, headers={"Authorization": f"Bearer {coach_token}"})
    assert p_res.status_code == 403

@pytest.mark.asyncio
async def test_max_players_limit(client: AsyncClient, admin_headers):
    # FT-04
    l_res = await client.post("/api/leagues", json={"name": "L_Max"}, headers=admin_headers)
    t_res = await client.post("/api/teams", json={"name": "T_Max", "league_id": l_res.json()["id"]}, headers=admin_headers)
    team_id = t_res.json()["id"]

    # Add 25 players
    for i in range(25):
        res = await client.post("/api/players", json={"first_name": "F", "last_name": f"L{i}", "number": i, "team_id": team_id}, headers=admin_headers)
        assert res.status_code == 200

    # Try 26th
    res_26 = await client.post("/api/players", json={"first_name": "F", "last_name": "L26", "number": 99, "team_id": team_id}, headers=admin_headers)
    assert res_26.status_code == 400
    assert "maximum limit of 25 players" in res_26.json()["detail"]
