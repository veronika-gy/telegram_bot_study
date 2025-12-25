from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from config import load_config

config = load_config()
# SQLite использует синхронный драйвер по умолчанию, для асинхронности нужен aiosqlite
engine = create_async_engine(f'sqlite+aiosqlite:///{config.db_name}', echo=True)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():
    """Создает все таблицы в базе данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Предоставляет асинхронную сессию для работы с БД."""
    async with AsyncSessionLocal() as session:
        yield session