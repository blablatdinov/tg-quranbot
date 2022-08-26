import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.future import Connection

from db.base import Base
from db.models import load_all_models
from settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

load_all_models()


async def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    context.configure(
        url=str(settings.alembic_db_url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run actual sync migrations.

    :param connection: connection to the database.
    """
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_async_engine(settings.alembic_db_url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

loop = asyncio.get_event_loop()
if context.is_offline_mode():
    task = run_migrations_offline()
else:
    task = run_migrations_online()

loop.run_until_complete(task)
