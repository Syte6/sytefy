import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from sytefy_backend.app.main import create_app
from sytefy_backend.core.database.base import Base
from sytefy_backend.core.database.session import get_db as real_get_db


@pytest_asyncio.fixture
async def test_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app = create_app()

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[real_get_db] = override_get_db  # type: ignore[arg-type]

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
