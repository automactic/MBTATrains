from sqlalchemy import Table, Column, Integer, String, MetaData


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