#!/usr/bin/env python3
"""
Initialize the SpaceDock database.

Creates the database (if needed), creates all tables, and stamps the
alembic version at head. Run once before starting services.

Usage:
    python scripts/db_init.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from KerbalStuff.database import (
    create_database,
    create_tables,
    drop_database,
    db,
)


def init_database() -> bool:
    """
    Initialize the database from scratch.
    Returns True if successful.
    """
    print("Creating database...")
    db_created = create_database()
    if db_created:
        print("Database created.")
    else:
        print("Database already exists.")

    print("Creating tables...")
    create_tables()
    db.commit()
    print("Tables created.")

    # Stamp alembic at head so it knows the schema is current
    import alembic.config
    from alembic import command as alembic_command

    alembic_cfg = alembic.config.Config("alembic.ini")
    alembic_command.stamp(alembic_cfg, "head")
    print("Alembic stamped at head.")

    return True


if __name__ == "__main__":
    try:
        success = init_database()
        if success:
            print("Database initialized successfully.")
            sys.exit(0)
        else:
            print("Failed to initialize database.")
            sys.exit(1)
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
