import asyncpg


async def create_pool() -> asyncpg.pool.Pool:
    return await asyncpg.create_pool(database='mbta')


async def create_connection() -> asyncpg.Connection:
    return await asyncpg.connect(database='mbta')


async def create_tables():
    # create table if not exist
    conn = await asyncpg.connect(database='postgres')
    records = await conn.fetch("SELECT * FROM pg_database WHERE datname = 'mbta';")
    if not records:
        await conn.execute("CREATE DATABASE mbta;")
    await conn.close()

    # create tables
    conn = await create_connection()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id varchar PRIMARY KEY,
            name varchar UNIQUE NOT NULL,
            description varchar,
            type varchar NOT NULL,
            sort_order integer UNIQUE NOT NULL,
            color varchar,
            text_color varchar
        );
        CREATE INDEX IF NOT EXISTS routes_name on routes(name);
        CREATE INDEX IF NOT EXISTS routes_sort_order on routes(sort_order);
    ''')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            label varchar PRIMARY KEY,
            status varchar NOT NULL,
            latitude float,
            longitude float,
            updated_at date,
            in_service bool NOT NULL DEFAULT false
        );
        CREATE INDEX IF NOT EXISTS vehicles_status on vehicles(status);
        CREATE INDEX IF NOT EXISTS vehicles_updated_at on vehicles(updated_at);
        CREATE INDEX IF NOT EXISTS vehicles_in_service on vehicles(in_service);
    ''')
    await conn.close()
