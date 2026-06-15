import pytest
from pydantic import ValidationError
import datetime
from schemas import (
    LeagueCreate, UserCreate, TeamCreate, PlayerCreate,
    ScheduleCreate, LocationCreate, GoalCreate, ScoreCreate, GameCreate,
    League, User, Team, Player, Schedule, Location, Goal, Score, Game
)

# --- League ---
def test_league_create_valid():
    league = LeagueCreate(name="Premier League")
    assert league.name == "Premier League"

def test_league_create_missing_name():
    with pytest.raises(ValidationError):
        LeagueCreate()

def test_league_create_invalid_type():
    with pytest.raises(ValidationError):
        LeagueCreate(name=None)

# --- User ---
def test_user_create_valid():
    user = UserCreate(username="testuser", role="admin", password="securepassword")
    assert user.username == "testuser"
    assert user.role == "admin"
    assert user.team_id is None

def test_user_create_with_team():
    user = UserCreate(username="coach1", role="coach", password="pwd", team_id=1)
    assert user.team_id == 1

def test_user_create_missing_fields():
    with pytest.raises(ValidationError):
        UserCreate(username="test") # missing role and password

# --- Team ---
def test_team_create_valid():
    team = TeamCreate(name="Arsenal", league_id=1)
    assert team.name == "Arsenal"
    assert team.league_id == 1

def test_team_create_missing_league():
    with pytest.raises(ValidationError):
        TeamCreate(name="Arsenal")

def test_team_create_invalid_league_id():
    with pytest.raises(ValidationError):
        TeamCreate(name="Arsenal", league_id="not_an_int")

# --- Player ---
def test_player_create_valid():
    player = PlayerCreate(first_name="John", last_name="Doe", number=10, team_id=1)
    assert player.first_name == "John"
    assert player.number == 10

def test_player_create_missing_fields():
    with pytest.raises(ValidationError):
        PlayerCreate(first_name="John", team_id=1) # missing last_name and number

def test_player_create_invalid_number():
    with pytest.raises(ValidationError):
        PlayerCreate(first_name="John", last_name="Doe", number="ten", team_id=1)

# --- Schedule ---
def test_schedule_create_valid():
    schedule = ScheduleCreate(name="Season 2024", league_id=2)
    assert schedule.name == "Season 2024"

def test_schedule_create_missing_fields():
    with pytest.raises(ValidationError):
        ScheduleCreate(league_id=2)

# --- Location ---
def test_location_create_valid():
    location = LocationCreate(name="Stadium A", time_zone_id="UTC")
    assert location.name == "Stadium A"

def test_location_create_missing_timezone():
    with pytest.raises(ValidationError):
        LocationCreate(name="Stadium A")

# --- Goal ---
def test_goal_create_valid():
    goal = GoalCreate(game_id=1, player_id=2, team_id=3, minute=45)
    assert goal.minute == 45

def test_goal_create_missing_minute():
    with pytest.raises(ValidationError):
        GoalCreate(game_id=1, player_id=2, team_id=3)

# --- Score ---
def test_score_create_valid():
    score = ScoreCreate(home_score=2, visitor_score=1)
    assert score.home_score == 2

def test_score_create_invalid_type():
    with pytest.raises(ValidationError):
        ScoreCreate(home_score="two", visitor_score=1)

# --- Game ---
def test_game_create_valid():
    dt = datetime.datetime.now()
    game = GameCreate(
        schedule_id=1, 
        home_team_id=2, 
        visitor_team_id=3, 
        location_id=4, 
        name="Finals",
        date_and_time=dt
    )
    assert game.name == "Finals"
    assert game.date_and_time == dt

def test_game_create_missing_fields():
    with pytest.raises(ValidationError):
        GameCreate(schedule_id=1, home_team_id=2, location_id=4) # missing visitor_team_id and name
