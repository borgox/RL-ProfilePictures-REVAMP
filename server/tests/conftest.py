import pytest
import pytest_asyncio
import asyncio
import sys
import os
from pathlib import Path
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from PIL import Image
import io

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from database.models import Base, Database
from cache.cache_manager import CacheManager
from config import settings
from routes import epic, platforms, admin, stats, bulk

# Test database URL - using SQLite instead of PostgreSQL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Override settings for testing
settings.database_url = TEST_DATABASE_URL
settings.cache_dir = "test_cache"
settings.rate_limit_requests = 1000  # High limit for testing
settings.debug = True


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create a test database engine."""
    # Create async engine for SQLite
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()
    
    # Remove test database file
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest_asyncio.fixture(scope="function")
async def test_db(test_db_engine) -> AsyncGenerator[Database, None]:
    """Create a test database instance."""
    db = Database()
    db.engine = test_db_engine
    db.async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    yield db
    
    # Cleanup is handled by test_db_engine fixture


@pytest_asyncio.fixture(scope="function")
async def test_cache() -> AsyncGenerator[CacheManager, None]:
    """Create a test cache manager."""
    cache = CacheManager(cache_dir="test_cache", max_memory_cache_size=100)
    await cache.initialize()
    
    yield cache
    
    # Cleanup test cache directory
    import shutil
    if os.path.exists("test_cache"):
        shutil.rmtree("test_cache")


@pytest.fixture(scope="function")
def client(test_db: Database, test_cache: CacheManager) -> Generator:
    """Create a test client with mocked dependencies."""
    # Set global instances in route modules
    epic.cache_manager = test_cache
    epic.database = test_db
    platforms.cache_manager = test_cache
    platforms.database = test_db
    admin.cache_manager = test_cache
    admin.database = test_db
    stats.database = test_db
    bulk.cache_manager = test_cache
    bulk.database = test_db
    
    # Create test client
    yield TestClient(app)


@pytest.fixture
def sample_avatar_png() -> bytes:
    """Create a sample PNG avatar for testing."""
    img = Image.new('RGBA', (48, 48), color=(73, 109, 137, 255))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


@pytest.fixture
def sample_avatar_jpg() -> bytes:
    """Create a sample JPG avatar for testing."""
    img = Image.new('RGB', (48, 48), color=(73, 109, 137))
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()


@pytest.fixture
def large_avatar_png() -> bytes:
    """Create a large PNG avatar for testing image processing."""
    img = Image.new('RGBA', (512, 512), color=(200, 100, 50, 255))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


@pytest_asyncio.fixture
async def populate_test_cache(test_cache: CacheManager, sample_avatar_png: bytes):
    """Populate cache with test data."""
    test_users = {
        "steam": ["76561198000000001", "76561198000000002", "76561198000000003"],
        "xbox": ["TestGamer1", "TestGamer2", "TestGamer3"],
        "psn": ["PSNUser1", "PSNUser2", "PSNUser3"],
        "epic": ["EpicUser1", "EpicUser2", "EpicUser3"],
        "switch": ["SwitchUser1", "SwitchUser2", "SwitchUser3"]
    }
    
    for platform, user_ids in test_users.items():
        for user_id in user_ids:
            await test_cache.set(platform, user_id, sample_avatar_png)
    
    return test_users


@pytest.fixture
def mock_steam_response():
    """Mock Steam API response."""
    return {
        "response": {
            "players": [{
                "steamid": "76561198000000001",
                "avatarfull": "https://example.com/avatar.jpg"
            }]
        }
    }


@pytest.fixture
def mock_xbox_response():
    """Mock Xbox API response."""
    return {
        "gamertag": "TestGamer",
        "displayPicRaw": "https://example.com/avatar.png"
    }


@pytest.fixture
def mock_psn_service():
    """Mock PSN service to avoid requiring NPSSO token."""
    from unittest.mock import Mock, AsyncMock, patch
    from services.avatar_services import PSNAvatarService
    
    mock_service = Mock(spec=PSNAvatarService)
    mock_service.get_processed_avatar = AsyncMock(return_value=None)
    
    with patch('routes.bulk.get_psn_service', return_value=mock_service):
        yield mock_service
