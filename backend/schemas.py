from pydantic import BaseModel
from typing import List, Optional
import datetime

# --- League ---
class LeagueBase(BaseModel):
    name: str

class LeagueCreate(LeagueBase):
    pass

class League(LeagueBase):
    id: int
    class Config:
        from_attributes = True

# --- User ---
class UserBase(BaseModel):
    username: str
    role: str
    team_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    hashed_password: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    team_id: Optional[int] = None


# --- Team ---
class TeamBase(BaseModel):
    name: str
    league_id: int

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int
    class Config:
        from_attributes = True

# --- Player ---
class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    number: int
    team_id: int

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int
    class Config:
        from_attributes = True

# --- Schedule ---
class ScheduleBase(BaseModel):
    name: str
    league_id: int

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    class Config:
        from_attributes = True

# --- Location ---
class LocationBase(BaseModel):
    name: str
    time_zone_id: str

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    class Config:
        from_attributes = True

# --- Goal ---
class GoalBase(BaseModel):
    game_id: int
    player_id: int
    team_id: int
    minute: int

class GoalCreate(GoalBase):
    pass

class Goal(GoalBase):
    id: int
    class Config:
        from_attributes = True

# --- Score ---
class ScoreBase(BaseModel):
    home_score: int
    visitor_score: int

class ScoreCreate(ScoreBase):
    pass

class Score(ScoreBase):
    game_id: int
    class Config:
        from_attributes = True

# --- Game ---
class GameBase(BaseModel):
    schedule_id: int
    home_team_id: int
    visitor_team_id: int
    location_id: int
    name: str
    date_and_time: Optional[datetime.datetime] = None

class GameCreate(GameBase):
    pass

class Game(GameBase):
    id: int
    score: Optional[Score] = None
    goals: List[Goal] = []
    class Config:
        from_attributes = True
