# import sys
# import os

# # Add project root to sys.path so Python finds models/config
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from models import Base  # 👈 import Base from models
# # from config import DB_URL
# from sqlalchemy import create_engine
# from alembic import context

# from dotenv import load_dotenv

# load_dotenv()

# DB_URL = os.getenv("DB_URL")

# # Alembic config
# config = context.config

# # DB connection
# target_metadata = Base.metadata


# def run_migrations_offline():
#     """Run migrations in 'offline' mode."""
#     url = DB_URL
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )

#     with context.begin_transaction():
#         context.run_migrations()


# def run_migrations_online():
#     """Run migrations in 'online' mode."""
#     connectable = create_engine(DB_URL)

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection,
#             target_metadata=target_metadata
#         )

#         with context.begin_transaction():
#             context.run_migrations()


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()




import sys
import os

from sqlalchemy import create_engine
from alembic import context
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Base  # Import Base from models

# Load .env
load_dotenv()

DB_URL = os.getenv("DB_URL")
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode'."""
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode'."""
    connectable = create_engine(DB_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

