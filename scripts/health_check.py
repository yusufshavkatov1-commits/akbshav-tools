import asyncio
from db.database import init_db, fetchval, close_db

async def main():
    await init_db(); value=await fetchval('SELECT 1'); await close_db()
    if value != 1: raise SystemExit(1)
    print('DATABASE_HEALTH_OK')

if __name__=='__main__': asyncio.run(main())
