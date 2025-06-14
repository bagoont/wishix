from sqlalchemy import select
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import SQLITE_URL, settings
from app.db.models import User, consts
from app.utils.passwords import hash_password

MAX_TRIES = 60 * 5
WAIT_SECONDS = 5

db_url = (
    URL.create(
        drivername=f"{settings.db.system}+{settings.db.driver}",
        username=settings.db.username,
        database=settings.db.db,
        password=settings.db.password,
        port=settings.db.port,
        host=settings.db.hostname,
    ).render_as_string(hide_password=False)
    if settings.db
    else SQLITE_URL
)
engine = create_async_engine(db_url)
session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def initial_data() -> None:
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.name == settings.superuser.name))
        if user is None:
            user = User(
                name=settings.superuser.name,
                hashed_password=hash_password(settings.superuser.password),
                is_active=True,
                role=consts.UserRole.SUPERUSER,
            )
            session.add(user)
            await session.commit()
            await session.close()
