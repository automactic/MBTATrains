from sqlalchemy import create_engine

from sql import metadata


def create_tables():
    # create table if not exist
    engine = create_engine('postgres://postgres@localhost/postgres')
    conn = engine.connect()
    conn = conn.execution_options(isolation_level="AUTOCOMMIT")
    results = conn.execute("SELECT * FROM pg_database WHERE datname = 'mbta';").fetchone()
    if not results:
        conn.execute("CREATE DATABASE mbta;")

    # create tables
    engine = create_engine('postgres://postgres@localhost/mbta')
    metadata.create_all(engine)
