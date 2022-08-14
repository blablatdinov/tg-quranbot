import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.future import Connection
from settings import settings
from db.base import Base
from db.models.ayat import Ayat
from db.models.sura import Sura

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

config = context.config


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = meta
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option('my_important_option')
# ... etc.


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
        url=str(settings.db_url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Run actual sync migrations.
    :param connection: connection to the database.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    uri = settings.DATABASE_URL
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    uri = uri.replace('postgresql', 'postgresql+asyncpg')
    connectable = create_async_engine(uri)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

loop = asyncio.get_event_loop()
if context.is_offline_mode():
    task = run_migrations_offline()
else:
    task = run_migrations_online()

loop.run_until_complete(task)
