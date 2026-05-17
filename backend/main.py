from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import List, Any
from sqlalchemy import select

import models, schemas, crud
from database import AsyncSessionLocal, engine, get_db
from auth import verify_password, get_password_hash, create_access_token, get_current_user, get_current_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
        
    # Create default admin if not exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.User).filter(models.User.username == "admin"))
        admin = result.scalar_one_or_none()
        if not admin:
            hashed_password = get_password_hash("admin")
            admin = models.User(username="admin", hashed_password=hashed_password, role="admin")
            db.add(admin)
            await db.commit()
            
    yield

app = FastAPI(title="Liga API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "role": user.role, "team_id": user.team_id})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "team_id": user.team_id}

# --- Users (Admin Only) ---
@app.get("/api/users", response_model=List[schemas.UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.get_users(db, skip=skip, limit=limit)

@app.post("/api/users", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    hashed_password = get_password_hash(user.password)
    return await crud.create_user(db, user, hashed_password)

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.delete_user(db, user_id)

# --- Leagues ---
@app.get("/api/leagues", response_model=List[schemas.League])
async def get_leagues(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_leagues(db, skip=skip, limit=limit)

@app.post("/api/leagues", response_model=schemas.League)
async def create_league(league: schemas.LeagueCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.create_league(db, league)

@app.put("/api/leagues/{league_id}", response_model=schemas.League)
async def update_league(league_id: int, league: schemas.LeagueCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.update_league(db, league_id, league)

@app.delete("/api/leagues/{league_id}")
async def delete_league(league_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.delete_league(db, league_id)

# --- Teams ---
@app.get("/api/teams", response_model=List[schemas.Team])
async def get_teams(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_teams(db, skip=skip, limit=limit)

@app.post("/api/teams", response_model=schemas.Team)
async def create_team(team: schemas.TeamCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.create_team(db, team)

@app.put("/api/teams/{team_id}", response_model=schemas.Team)
async def update_team(team_id: int, team: schemas.TeamCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.update_team(db, team_id, team)

@app.delete("/api/teams/{team_id}")
async def delete_team(team_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.delete_team(db, team_id)

# --- Players ---
@app.get("/api/players", response_model=List[schemas.Player])
async def get_players(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_players(db, skip=skip, limit=limit)

@app.post("/api/players", response_model=schemas.Player)
async def create_player(player: schemas.PlayerCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "coach" and current_user.team_id != player.team_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this team")
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="Users cannot create players")
    return await crud.create_player(db, player)

@app.put("/api/players/{player_id}", response_model=schemas.Player)
async def update_player(player_id: int, player: schemas.PlayerCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "coach" and current_user.team_id != player.team_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this team")
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="Users cannot update players")
    return await crud.update_player(db, player_id, player)

@app.delete("/api/players/{player_id}")
async def delete_player(player_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Player).filter(models.Player.id == player_id))
    db_player = result.scalar_one_or_none()
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    if current_user.role == "coach" and current_user.team_id != db_player.team_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this team")
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="Users cannot delete players")
    return await crud.delete_player(db, player_id)

# --- Schedules ---
@app.get("/api/schedules", response_model=List[schemas.Schedule])
async def get_schedules(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_schedules(db, skip=skip, limit=limit)

@app.post("/api/schedules", response_model=schemas.Schedule)
async def create_schedule(schedule: schemas.ScheduleCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.create_schedule(db, schedule)

# --- Locations ---
@app.get("/api/locations", response_model=List[schemas.Location])
async def get_locations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_locations(db, skip=skip, limit=limit)

@app.post("/api/locations", response_model=schemas.Location)
async def create_location(location: schemas.LocationCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.create_location(db, location)

@app.delete("/api/locations/{location_id}")
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    return await crud.delete_location(db, location_id)

# --- Games ---
@app.get("/api/games", response_model=List[schemas.Game])
async def get_games(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_games(db, skip=skip, limit=limit)

@app.post("/api/games", response_model=schemas.Game)
async def create_game(game: schemas.GameCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "coach" and (current_user.team_id != game.home_team_id and current_user.team_id != game.visitor_team_id):
        raise HTTPException(status_code=403, detail="Coach can only create games for their team")
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="Users cannot create games")
    return await crud.create_game(db, game)

@app.delete("/api/games/{game_id}")
async def delete_game(game_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Game).filter(models.Game.id == game_id))
    db_game = result.scalar_one_or_none()
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")
    if current_user.role == "coach" and (current_user.team_id != db_game.home_team_id and current_user.team_id != db_game.visitor_team_id):
        raise HTTPException(status_code=403, detail="Coach can only delete their own games")
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="Users cannot delete games")
    return await crud.delete_game(db, game_id)

# --- Scores ---
@app.post("/api/games/{game_id}/score", response_model=schemas.Score)
async def set_score(game_id: int, score: schemas.ScoreCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "coach":
        result = await db.execute(select(models.Game).filter(models.Game.id == game_id))
        game = result.scalar_one_or_none()
        if not game or (game.home_team_id != current_user.team_id and game.visitor_team_id != current_user.team_id):
            raise HTTPException(status_code=403, detail="Not enough permissions for this game")
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="Users cannot update scores")
    return await crud.set_score(db, game_id, score)

# --- Goals ---
@app.post("/api/goals", response_model=schemas.Goal)
async def add_goal(goal: schemas.GoalCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "coach" and current_user.team_id != goal.team_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this team")
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="Users cannot add goals")
    return await crud.add_goal(db, goal)

# --- Analytics ---
@app.get("/api/stats/teams", response_model=List[Any])
async def get_best_teams(db: AsyncSession = Depends(get_db)):
    return await crud.get_best_teams(db)

@app.get("/api/stats/players", response_model=List[Any])
async def get_best_players(db: AsyncSession = Depends(get_db)):
    return await crud.get_best_players(db)

@app.get("/api/stats/best-player-vs-team/{team_id}")
async def get_best_player_vs_team(team_id: int, db: AsyncSession = Depends(get_db)):
    result = await crud.get_best_player_vs_team(db, team_id)
    if not result:
        raise HTTPException(status_code=404, detail="No data available")
    return result

@app.get("/api/stats/best-team-vs-team/{team_id}")
async def get_best_team_vs_team(team_id: int, db: AsyncSession = Depends(get_db)):
    result = await crud.get_best_team_vs_team(db, team_id)
    if not result:
        raise HTTPException(status_code=404, detail="No data available")
    return result
