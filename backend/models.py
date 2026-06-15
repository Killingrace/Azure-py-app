from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class League(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    schedules = relationship("Schedule", back_populates="league", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="league", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # 'admin', 'coach', 'user'
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True) # for coaches


class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    name = Column(String)

    league = relationship("League", back_populates="schedules")
    games = relationship("Game", back_populates="schedule", cascade="all, delete-orphan")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    name = Column(String, unique=True, index=True)

    league = relationship("League", back_populates="teams")
    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    first_name = Column(String)
    last_name = Column(String)
    number = Column(Integer)

    team = relationship("Team", back_populates="players")

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    time_zone_id = Column(String)

    games = relationship("Game", back_populates="location")

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    visitor_team_id = Column(Integer, ForeignKey("teams.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    name = Column(String)
    date_and_time = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    schedule = relationship("Schedule", back_populates="games")
    home_team = relationship("Team", foreign_keys=[home_team_id])
    visitor_team = relationship("Team", foreign_keys=[visitor_team_id])
    location = relationship("Location", back_populates="games")
    score = relationship("Score", back_populates="game", uselist=False, cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="game", cascade="all, delete-orphan")

class Score(Base):
    __tablename__ = "scores"
    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)
    home_score = Column(Integer, default=0)
    visitor_score = Column(Integer, default=0)

    game = relationship("Game", back_populates="score")

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    minute = Column(Integer)

    game = relationship("Game", back_populates="goals")
    player = relationship("Player")
    team = relationship("Team")
