import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

import os
import importlib
import pkgutil

from alembic import context

from app.core.config import settings
from app.db.base_class import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
safe_url = settings.get_database_url.replace('%', '%%')
config.set_main_option("sqlalchemy.url", safe_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
def import_all_models():
    # Define the path to your models folder
    models_package = os.path.join(os.path.dirname(__file__), '../app/db/models')

    # Iterate over all the modules in the models directory and import them
    module_names = [name for _, name, _ in pkgutil.iter_modules([models_package])]
    print(module_names)

    # Import each model module dynamically
    for module_name in module_names:
        # Dynamically import the module
        importlib.import_module(f'app.db.models.{module_name}')


# Import all models to ensure they are registered with SQLAlchemy's Base
import_all_models()

# Set target_metadata to Base.metadata for Alembic to use
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
