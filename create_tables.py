import asyncio
from app.database import Base, _get_engine
from app.models import User, Category, Product, Order, OrderItem, Review

async def create_tables():
    print(f"Tables registered with Base: {[table.name for table in Base.metadata.tables.values()]}")
    async with _get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created successfully!")

asyncio.run(create_tables())
