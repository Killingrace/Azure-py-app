import os
import pytest
import pytest_asyncio
from httpx import AsyncClient

# Ustawienie bazy danych w pamięci (SQLite) przed importem modułów backendu
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import engine, AsyncSessionLocal, Base
import models
from auth import create_access_token, get_password_hash

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Tworzenie tabel przed każdym testem i czyszczenie po teście."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Tworzenie domyślnych użytkowników testowych
    async with AsyncSessionLocal() as db:
        admin_pwd = get_password_hash("admin")
        db.add(models.User(username="admin", hashed_password=admin_pwd, role="admin"))
        
        # Trener bez przypisanej drużyny (team_id=None), aby ominąć błędy kluczy obcych na pustej bazie
        coach_pwd = get_password_hash("coach")
        db.add(models.User(username="coach1", hashed_password=coach_pwd, role="coach", team_id=None))
        
        await db.commit()
        
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client():
    # Używamy ASGITransport dla kompatybilności z nowym httpx
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

# --- Auth Fixtures ---

@pytest.fixture
def admin_token():
    return create_access_token(data={"sub": "admin", "role": "admin"})

@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def coach_token():
    return create_access_token(data={"sub": "coach1", "role": "coach", "team_id": 1})

@pytest.fixture
def coach_headers(coach_token):
    return {"Authorization": f"Bearer {coach_token}"}

@pytest.fixture
def coach2_token():
    return create_access_token(data={"sub": "coach2", "role": "coach", "team_id": 2})

@pytest.fixture
def coach2_headers(coach2_token):
    return {"Authorization": f"Bearer {coach2_token}"}

@pytest.fixture
def user_token():
    return create_access_token(data={"sub": "user1", "role": "user"})

@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}
