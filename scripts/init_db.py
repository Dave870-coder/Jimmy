"""Initialize database with admin user and demo data."""

import asyncio
import uuid
from datetime import datetime

from src.database import AsyncSessionLocal
from src.database.models import User, Message, Memory
from src.security.auth import hash_password


async def init_admin_user():
    """Create initial admin user."""
    async with AsyncSessionLocal() as session:
        admin_user = User(
            id=str(uuid.uuid4()),
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            first_name="Admin",
            last_name="User",
            is_active=True,
            is_admin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(admin_user)
        await session.commit()
        print(f"✅ Admin user created: {admin_user.email}")


async def init_demo_data():
    """Create demo data for testing."""
    async with AsyncSessionLocal() as session:
        # Create demo user
        demo_user = User(
            id=str(uuid.uuid4()),
            username="demo",
            email="demo@example.com",
            password_hash=hash_password("demo123"),
            first_name="Demo",
            last_name="User",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(demo_user)
        await session.commit()
        print(f"✅ Demo user created: {demo_user.email}")
        
        # Create demo messages
        for i in range(5):
            message = Message(
                id=str(uuid.uuid4()),
                user_id=demo_user.id,
                content=f"Demo message {i+1}",
                message_type="text",
                source="api",
                created_at=datetime.utcnow(),
            )
            session.add(message)
        
        await session.commit()
        print(f"✅ Demo messages created")


async def main():
    """Run initialization."""
    print("🚀 Initializing database...")
    await init_admin_user()
    await init_demo_data()
    print("✅ Database initialization completed!")


if __name__ == "__main__":
    asyncio.run(main())
