from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import models
import schemas

# --- Users ---
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(username=user.username, role=user.role, team_id=user.team_id, hashed_password=hashed_password)
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Username already registered or invalid team_id")

async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user:
        try:
            await db.delete(db_user)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Cannot delete user due to existing relationships.")
    return db_user

# --- League ---
async def get_leagues(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.League).offset(skip).limit(limit))
    return result.scalars().all()

async def create_league(db: AsyncSession, league: schemas.LeagueCreate):
    db_league = models.League(name=league.name)
    db.add(db_league)
    await db.commit()
    await db.refresh(db_league)
    return db_league

async def update_league(db: AsyncSession, league_id: int, league: schemas.LeagueCreate):
    result = await db.execute(select(models.League).filter(models.League.id == league_id))
    db_league = result.scalar_one_or_none()
    if db_league:
        db_league.name = league.name
        await db.commit()
        await db.refresh(db_league)
    return db_league

async def delete_league(db: AsyncSession, league_id: int):
    result = await db.execute(select(models.League).filter(models.League.id == league_id))
    db_league = result.scalar_one_or_none()
    if db_league:
        try:
            await db.delete(db_league)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Cannot delete league. It may have associated teams or schedules.")
    return db_league

# --- Team ---
async def get_teams(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Team).offset(skip).limit(limit))
    return result.scalars().all()

async def create_team(db: AsyncSession, team: schemas.TeamCreate):
    db_team = models.Team(**team.model_dump())
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team

async def update_team(db: AsyncSession, team_id: int, team: schemas.TeamCreate):
    result = await db.execute(select(models.Team).filter(models.Team.id == team_id))
    db_team = result.scalar_one_or_none()
    if db_team:
        db_team.name = team.name
        db_team.league_id = team.league_id
        await db.commit()
        await db.refresh(db_team)
    return db_team

async def delete_team(db: AsyncSession, team_id: int):
    result = await db.execute(select(models.Team).filter(models.Team.id == team_id))
    db_team = result.scalar_one_or_none()
    if db_team:
        try:
            await db.delete(db_team)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Cannot delete team. It may be part of existing games.")
    return db_team

# --- Player ---
async def get_players(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Player).offset(skip).limit(limit))
    return result.scalars().all()

async def create_player(db: AsyncSession, player: schemas.PlayerCreate):
    # Validation: Ensure team has less than 25 players
    result = await db.execute(select(func.count(models.Player.id)).filter(models.Player.team_id == player.team_id))
    current_players = result.scalar_one()
    if current_players >= 25:
        raise HTTPException(status_code=400, detail="Team has reached the maximum limit of 25 players.")

    db_player = models.Player(**player.model_dump())
    db.add(db_player)
    await db.commit()
    await db.refresh(db_player)
    return db_player

async def update_player(db: AsyncSession, player_id: int, player: schemas.PlayerCreate):
    result = await db.execute(select(models.Player).filter(models.Player.id == player_id))
    db_player = result.scalar_one_or_none()
    if db_player:
        db_player.first_name = player.first_name
        db_player.last_name = player.last_name
        db_player.number = player.number
        db_player.team_id = player.team_id
        await db.commit()
        await db.refresh(db_player)
    return db_player

async def delete_player(db: AsyncSession, player_id: int):
    result = await db.execute(select(models.Player).filter(models.Player.id == player_id))
    db_player = result.scalar_one_or_none()
    if db_player:
        try:
            await db.delete(db_player)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Cannot delete player. They may have registered goals.")
    return db_player

# --- Schedule ---
async def get_schedules(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Schedule).offset(skip).limit(limit))
    return result.scalars().all()

async def create_schedule(db: AsyncSession, schedule: schemas.ScheduleCreate):
    db_schedule = models.Schedule(**schedule.model_dump())
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule

# --- Location ---
async def get_locations(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Location).offset(skip).limit(limit))
    return result.scalars().all()

async def create_location(db: AsyncSession, location: schemas.LocationCreate):
    db_location = models.Location(**location.model_dump())
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)
    return db_location

async def delete_location(db: AsyncSession, location_id: int):
    result = await db.execute(select(models.Location).filter(models.Location.id == location_id))
    db_location = result.scalar_one_or_none()
    if db_location:
        try:
            await db.delete(db_location)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Cannot delete location. It is used in existing games.")
    return db_location

# --- Game ---
async def get_games(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Game)
        .options(selectinload(models.Game.score), selectinload(models.Game.goals))
        .offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_game(db: AsyncSession, game: schemas.GameCreate):
    home_result = await db.execute(select(func.count(models.Player.id)).filter(models.Player.team_id == game.home_team_id))
    home_players = home_result.scalar_one()
    if home_players < 11:
        raise HTTPException(status_code=400, detail="Home team does not have enough players (min 11).")
        
    visitor_result = await db.execute(select(func.count(models.Player.id)).filter(models.Player.team_id == game.visitor_team_id))
    visitor_players = visitor_result.scalar_one()
    if visitor_players < 11:
        raise HTTPException(status_code=400, detail="Visitor team does not have enough players (min 11).")

    db_game = models.Game(**game.model_dump())
    db.add(db_game)
    await db.commit()
    
    # Eager loading aby Pydantic nie wyrzucał MissingGreenlet
    result = await db.execute(
        select(models.Game)
        .options(selectinload(models.Game.score), selectinload(models.Game.goals))
        .filter(models.Game.id == db_game.id)
    )
    return result.scalar_one()

async def delete_game(db: AsyncSession, game_id: int):
    result = await db.execute(select(models.Game).filter(models.Game.id == game_id))
    db_game = result.scalar_one_or_none()
    if db_game:
        try:
            await db.delete(db_game)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Cannot delete game. It may have associated scores or goals.")
    return db_game

# --- Score ---
async def set_score(db: AsyncSession, game_id: int, score: schemas.ScoreCreate):
    result = await db.execute(select(models.Score).filter(models.Score.game_id == game_id))
    db_score = result.scalar_one_or_none()
    if db_score:
        db_score.home_score = score.home_score
        db_score.visitor_score = score.visitor_score
    else:
        db_score = models.Score(game_id=game_id, home_score=score.home_score, visitor_score=score.visitor_score)
        db.add(db_score)
    await db.commit()
    await db.refresh(db_score)
    return db_score

# --- Goal ---
async def add_goal(db: AsyncSession, goal: schemas.GoalCreate):
    db_goal = models.Goal(**goal.model_dump())
    db.add(db_goal)
    await db.commit()
    await db.refresh(db_goal)
    return db_goal

# --- Analytics ---

async def get_best_teams(db: AsyncSession):
    result = await db.execute(select(models.Game).options(selectinload(models.Game.score)))
    games = result.scalars().all()
    stats = {}

    teams_result = await db.execute(select(models.Team))
    teams = teams_result.scalars().all()
    for t in teams:
        stats[t.id] = {"id": t.id, "name": t.name, "points": 0, "wins": 0, "draws": 0, "losses": 0, "goal_diff": 0}

    for game in games:
        if game.score:
            home = game.home_team_id
            visitor = game.visitor_team_id
            hs = game.score.home_score
            vs = game.score.visitor_score
            
            if home in stats: stats[home]["goal_diff"] += (hs - vs)
            if visitor in stats: stats[visitor]["goal_diff"] += (vs - hs)

            if hs > vs:
                if home in stats:
                    stats[home]["points"] += 3
                    stats[home]["wins"] += 1
                if visitor in stats:
                    stats[visitor]["losses"] += 1
            elif vs > hs:
                if visitor in stats:
                    stats[visitor]["points"] += 3
                    stats[visitor]["wins"] += 1
                if home in stats:
                    stats[home]["losses"] += 1
            else:
                if home in stats:
                    stats[home]["points"] += 1
                    stats[home]["draws"] += 1
                if visitor in stats:
                    stats[visitor]["points"] += 1
                    stats[visitor]["draws"] += 1

    sorted_teams = sorted(stats.values(), key=lambda x: (x["points"], x["goal_diff"]), reverse=True)
    return sorted_teams

async def get_best_players(db: AsyncSession):
    stmt = select(
        models.Goal.player_id, 
        func.count(models.Goal.id).label('goal_count')
    ).group_by(models.Goal.player_id).order_by(desc('goal_count'))
    
    result = await db.execute(stmt)
    goal_data = result.all()

    player_stats = []
    for row in goal_data:
        p_result = await db.execute(select(models.Player).options(selectinload(models.Player.team)).filter(models.Player.id == row.player_id))
        player = p_result.scalar_one_or_none()
        if player:
            gp_result = await db.execute(
                select(func.count(models.Game.id)).filter(
                    or_(models.Game.home_team_id == player.team_id, models.Game.visitor_team_id == player.team_id)
                )
            )
            games_played = gp_result.scalar_one()
            avg_goals = round(row.goal_count / games_played, 2) if games_played > 0 else 0
            
            player_stats.append({
                "id": player.id,
                "first_name": player.first_name,
                "last_name": player.last_name,
                "team_name": player.team.name if player.team else "",
                "total_goals": row.goal_count,
                "avg_goals": avg_goals
            })

    return sorted(player_stats, key=lambda x: x["total_goals"], reverse=True)

async def get_best_player_vs_team(db: AsyncSession, team_id: int):
    subq = select(models.Game.id).filter(
        or_(models.Game.home_team_id == team_id, models.Game.visitor_team_id == team_id)
    ).scalar_subquery()

    stmt = select(
        models.Goal.player_id,
        func.count(models.Goal.id).label('goal_count')
    ).filter(
        models.Goal.game_id.in_(subq),
        models.Goal.team_id != team_id
    ).group_by(models.Goal.player_id).order_by(desc('goal_count'))

    result = await db.execute(stmt)
    row = result.first()

    if not row:
        return None

    p_result = await db.execute(select(models.Player).filter(models.Player.id == row.player_id))
    player = p_result.scalar_one_or_none()
    if player:
        player_schema = schemas.Player.model_validate(player)
        return {"player": player_schema, "goals": row.goal_count}
    return None

async def get_best_team_vs_team(db: AsyncSession, team_id: int):
    result = await db.execute(
        select(models.Game)
        .options(selectinload(models.Game.score))
        .filter(or_(models.Game.home_team_id == team_id, models.Game.visitor_team_id == team_id))
    )
    games = result.scalars().all()

    stats = {}
    for game in games:
        if not game.score: continue
        
        opponent_id = game.visitor_team_id if game.home_team_id == team_id else game.home_team_id
        if opponent_id not in stats:
            stats[opponent_id] = {"points": 0, "goal_diff": 0, "goals_scored": 0}

        team_goals = game.score.home_score if game.home_team_id == team_id else game.score.visitor_score
        opp_goals = game.score.visitor_score if game.home_team_id == team_id else game.score.home_score

        stats[opponent_id]["goals_scored"] += opp_goals
        stats[opponent_id]["goal_diff"] += (opp_goals - team_goals)

        if opp_goals > team_goals:
            stats[opponent_id]["points"] += 3
        elif opp_goals == team_goals:
            stats[opponent_id]["points"] += 1

    if not stats:
        return None

    best_opponent_id = sorted(stats.items(), key=lambda x: (x[1]["points"], x[1]["goal_diff"], x[1]["goals_scored"]), reverse=True)[0][0]
    t_result = await db.execute(select(models.Team).filter(models.Team.id == best_opponent_id))
    best_team = t_result.scalar_one_or_none()
    if best_team:
        team_schema = schemas.Team.model_validate(best_team)
        return {"team": team_schema, "stats": stats[best_opponent_id]}
    return None
