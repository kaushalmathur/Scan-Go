import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio

# Adjust these imports depending on exact backend package layout.
from .main import app
from .database import Base, get_db
from .services import auth
from .models import Merchant

# Use a test-specific database URI
TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/scango_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def test_db():
    """Builds and tears down the test database tables."""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Need a default merchant for the users to register under
    merchant = Merchant(name="Test Store", location="123 Test Ave")
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def override_get_db(test_db):
    """Overrides the FastAPI dependency to use the test session."""
    def _get_test_db():
        try:
            yield test_db
        finally:
            pass
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
async def client(override_get_db):
    """Yields an async httpx client tied to the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="module")
async def auth_token(client, test_db):
    """Helper to return a valid authorization header token."""
    # Register explicitly for the token
    await client.post(
        "/auth/register",
        json={"email": "token@test.com", "password": "password123", "store_id": 1}
    )
    res = await client.post(
        "/auth/login",
        data={"username": "token@test.com", "password": "password123"} # OAuth2 structure
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
