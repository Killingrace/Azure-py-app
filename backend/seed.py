import os
import bcrypt
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, AsyncSessionLocal
import models

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def seed():
    # Recreate tables asynchronously
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Admin & Coach
        admin = models.User(username="admin", hashed_password=get_password_hash("admin"), role="admin")
        db.add(admin)
        await db.commit()

        # 2. League
        league = models.League(name="Premier League 2026")
        db.add(league)
        await db.commit()
        await db.refresh(league)

        # 3. Default Schedule
        schedule = models.Schedule(name="Default Season 2026", league_id=league.id)
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)

        # 4. Teams
        teams_data = ["Arsenal", "Chelsea", "Manchester City", "Liverpool"]
        teams = []
        for t_name in teams_data:
            t = models.Team(name=t_name, league_id=league.id)
            db.add(t)
            await db.commit()
            await db.refresh(t)
            teams.append(t)

        # 5. Coach
        coach = models.User(username="coach", hashed_password=get_password_hash("coach"), role="coach", team_id=teams[0].id)
        db.add(coach)
        await db.commit()

        # 6. Players (11 per team)
        players = []
        for idx, t in enumerate(teams):
            for p_num in range(1, 12):
                p = models.Player(
                    first_name=f"Player{p_num}",
                    last_name=f"Team{idx}",
                    number=p_num,
                    team_id=t.id
                )
                db.add(p)
                players.append(p)
        await db.commit()

        # 7. Locations
        loc1 = models.Location(name="Stadium A", time_zone_id="UTC")
        loc2 = models.Location(name="Stadium B", time_zone_id="UTC")
        db.add(loc1)
        db.add(loc2)
        await db.commit()
        await db.refresh(loc1)

        # 8. Games & Scores & Goals
        game1 = models.Game(
            schedule_id=schedule.id,
            home_team_id=teams[0].id,
            visitor_team_id=teams[1].id,
            location_id=loc1.id,
            name="Matchday 1: ARS vs CHE"
        )
        db.add(game1)
        await db.commit()
        await db.refresh(game1)

        score1 = models.Score(game_id=game1.id, home_score=2, visitor_score=1)
        db.add(score1)

        # Goals for game1 (2 for Arsenal, 1 for Chelsea)
        goal1 = models.Goal(game_id=game1.id, team_id=teams[0].id, player_id=players[0].id, minute=15)
        goal2 = models.Goal(game_id=game1.id, team_id=teams[0].id, player_id=players[1].id, minute=45)
        goal3 = models.Goal(game_id=game1.id, team_id=teams[1].id, player_id=players[11].id, minute=80)
        db.add_all([goal1, goal2, goal3])
        await db.commit()

        print("Database successfully seeded asynchronously!")

if __name__ == "__main__":
    asyncio.run(seed())
