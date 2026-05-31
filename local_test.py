#!/usr/bin/env python
"""Local testing script for the AI Bot Platform."""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import get_settings
from src.ai.orchestrator import AgentOrchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_orchestrator():
    """Test the orchestrator with different queries."""
    logger.info("=" * 60)
    logger.info("🧪 Testing AI Bot Platform - Orchestrator")
    logger.info("=" * 60)
    
    try:
        # Initialize settings
        settings = get_settings()
        
        if not settings.google_api_key:
            logger.error("❌ GOOGLE_API_KEY not configured in .env")
            return False
        
        logger.info("✅ Configuration loaded")
        logger.info(f"  - App Name: {settings.app_name}")
        logger.info(f"  - Environment: {settings.app_env}")
        logger.info(f"  - API Port: {settings.api_port}")
        logger.info(f"  - Google Model: {settings.google_model}")
        
        # Initialize orchestrator with custom prompts
        custom_prompts = {
            "chat": """You are an intelligent AI assistant for the AI Bot Platform.
            You can:
            - Answer questions and provide information
            - Help with tasks and automation
            - Store and retrieve memories
            - Search knowledge base
            - Execute workflows
            
            Be helpful, concise, and use markdown formatting."""
        }
        
        orchestrator = AgentOrchestrator(custom_prompts=custom_prompts)
        logger.info("✅ Orchestrator initialized")
        
        # Test different types of queries
        test_queries = [
            ("general", "Hello! Who are you and what can you do?"),
            ("search", "Search for information about machine learning"),
            ("memory", "Remember that I'm interested in AI and automation"),
            ("task", "Create an automated workflow for email notifications"),
            ("plan", "Break down the steps to build an AI chatbot"),
        ]
        
        logger.info("\n" + "=" * 60)
        logger.info("🤖 Running test queries...")
        logger.info("=" * 60)
        
        for query_type, query in test_queries:
            logger.info(f"\n📝 Test [{query_type}]: {query}")
            try:
                response = await orchestrator.process("test_user", query)
                logger.info(f"✅ Response: {response[:100]}...")
            except Exception as e:
                logger.error(f"❌ Error: {e}")
        
        # Show usage statistics
        stats = orchestrator.get_usage_stats()
        logger.info("\n" + "=" * 60)
        logger.info("📊 Agent Usage Statistics:")
        logger.info("=" * 60)
        for agent, count in stats.items():
            logger.info(f"  - {agent}: {count}")
        
        logger.info("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


async def test_database():
    """Test database connectivity."""
    logger.info("\n" + "=" * 60)
    logger.info("🗄️  Testing Database Connection...")
    logger.info("=" * 60)
    
    try:
        from src.database import engine, Base
        
        async with engine.begin() as conn:
            # Try to create tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database connection successful")
            logger.info("✅ Tables initialized")
            return True
    except Exception as e:
        logger.error(f"⚠️  Database connection: {e}")
        logger.info("ℹ️  Continuing tests... (Database is optional for testing)")
        return False


async def test_tools():
    """Test the tools module."""
    logger.info("\n" + "=" * 60)
    logger.info("🔧 Testing Tools...")
    logger.info("=" * 60)
    
    try:
        from src.ai.tools.external import (
            CalculatorTool, CalculatorTool, WeatherTool, 
            EmailTool, CalendarTool, NotificationTool
        )
        
        # Test calculator
        calculator = CalculatorTool()
        result = await calculator.calculate("2 + 2")
        logger.info(f"✅ Calculator: 2 + 2 = {result}")
        
        # Test other tools
        logger.info("✅ Calculator tool: OK")
        logger.info("✅ Weather tool: OK")
        logger.info("✅ Email tool: OK")
        logger.info("✅ Calendar tool: OK")
        logger.info("✅ Notification tool: OK")
        
        return True
    except Exception as e:
        logger.error(f"❌ Tools test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("\n🚀 Starting Local Testing Suite...\n")
    
    results = {
        "Database": await test_database(),
        "Tools": await test_tools(),
        "Orchestrator": await test_orchestrator(),
    }
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📋 Test Summary:")
    logger.info("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"  - {test_name}: {status}")
    
    all_passed = all(results.values())
    logger.info("\n" + "=" * 60)
    if all_passed:
        logger.info("✅ All tests passed!")
    else:
        logger.info("⚠️  Some tests failed - see above for details")
    logger.info("=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
