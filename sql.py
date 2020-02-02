from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy import create_engine
import asyncpg


metadata = MetaData()
routes = Table(
    'routes', metadata,
    Column('id', String, primary_key=True),
    Column('name', String),
    Column('description', String),
    Column('type', String),
    Column('sort_order', Integer),
    Column('color', String),
    Column('text_color', String),
)


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


async def create_asyncpg_conn() -> asyncpg.Connection:
    return await asyncpg.connect('postgres://postgres@localhost/mbta')