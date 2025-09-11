# FastAPI + Alembic + PostgreSQL

This project uses **FastAPI**, **SQLAlchemy**, **Alembic**, and
**PostgreSQL** for database migrations.

## 🚀 Setup Instructions

### 1. Install dependencies

``` bash
pip install fastapi uvicorn sqlalchemy psycopg2 alembic
```

### 2. Initialize Alembic (only once)

``` bash
alembic init alembic
```

### 3. Configure Alembic

-   Open `alembic.ini` and update the `sqlalchemy.url` with your
    PostgreSQL connection string.

Example:

    sqlalchemy.url = postgresql+psycopg2://username:password@localhost:5432/your_db

### 4. Create a new migration (after model changes)

``` bash
alembic revision --autogenerate -m "create users table"
```

## update the model 
```
alembic revision --autogenerate -m "update product schema"
```

### 5. Apply migrations to database

``` bash
alembic upgrade head
```

### 6. Downgrade (rollback last migration)

``` bash
alembic downgrade -1
```

### 7. Check migration history

``` bash
alembic history
```

### 8. Show current database revision

``` bash
alembic current
```

### 9. Create a new table (example)

-   Add your new table model in `models.py`
-   Run:

``` bash
alembic revision --autogenerate -m "add new table"
alembic upgrade head
```

### 10. Update existing table (example: add column)

-   Modify your model in `models.py`
-   Run:

``` bash
alembic revision --autogenerate -m "add new column to users"
alembic upgrade head
```

------------------------------------------------------------------------

## ✅ Common Commands

  Action                  Command
  ----------------------- ------------------------------------------------
  Create migration        `alembic revision --autogenerate -m "message"`
  Apply migration         `alembic upgrade head`
  Rollback migration      `alembic downgrade -1`
  Show history            `alembic history`
  Show current revision   `alembic current`

------------------------------------------------------------------------

## 📌 Notes

-   Always run migrations after updating your models.
-   Use meaningful migration messages for better tracking.
