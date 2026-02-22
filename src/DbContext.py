import asyncpg

pool = None

async def init_db():
    global pool

    pool = await asyncpg.create_pool(
        database = 'linguamatebot',
        user = 'postgres',
        password = '123'
    )
