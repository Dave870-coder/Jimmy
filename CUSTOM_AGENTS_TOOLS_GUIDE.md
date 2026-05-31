"""
Custom Agents and Tools Usage Guide

This guide shows how to use and extend the custom agents and tools
provided by the AI Bot Platform.
"""

# ============================================================================
# 1. USING BUILT-IN CUSTOM AGENTS
# ============================================================================

from src.ai.agents.custom import custom_registry

# Example 1: Using the Summary Agent
async def example_summary_agent():
    """Example using the Summary Agent."""
    summary_agent = custom_registry.get_agent("summary")
    
    long_content = "This is a very long content that needs to be summarized..."
    summary = await summary_agent.process(long_content, max_length=100)
    print(f"Summary: {summary}")


# Example 2: Using the Analysis Agent
async def example_analysis_agent():
    """Example using the Analysis Agent."""
    analysis_agent = custom_registry.get_agent("analysis")
    
    data = [
        {"user_id": 1, "action": "login", "timestamp": "2026-05-31 10:00:00"},
        {"user_id": 2, "action": "message", "timestamp": "2026-05-31 10:05:00"},
        {"user_id": 1, "action": "message", "timestamp": "2026-05-31 10:10:00"},
    ]
    
    analysis = await analysis_agent.analyze(data)
    print(f"Analysis: {analysis}")


# Example 3: Using the Recommendation Agent
async def example_recommendation_agent():
    """Example using the Recommendation Agent."""
    recommendation_agent = custom_registry.get_agent("recommendation")
    
    user_prefs = {
        "interests": ["machine learning", "python", "AI"],
        "experience_level": "intermediate",
    }
    
    recommendations = await recommendation_agent.get_recommendations(user_prefs)
    print(f"Recommendations: {recommendations}")


# Example 4: Using the Validation Agent
async def example_validation_agent():
    """Example using the Validation Agent."""
    validation_agent = custom_registry.get_agent("validation")
    
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
    }
    
    validation_result = await validation_agent.validate(user_data)
    print(f"Validation: {validation_result}")


# Example 5: Using the Integration Agent
async def example_integration_agent():
    """Example using the Integration Agent."""
    integration_agent = custom_registry.get_agent("integration")
    
    result = await integration_agent.fetch_from_service(
        service_name="external_api",
        endpoint="/api/v1/users",
        params={"page": 1, "limit": 10}
    )
    print(f"Integration Result: {result}")


# ============================================================================
# 2. USING BUILT-IN CUSTOM TOOLS
# ============================================================================

from src.ai.tools.custom import custom_tools_repo

# Example 1: Using the Webhook Tool
async def example_webhook_tool():
    """Example using the Webhook Tool."""
    webhook_tool = custom_tools_repo.get_tool("webhook")
    
    data = {
        "event": "user_signup",
        "user_id": 123,
        "timestamp": "2026-05-31T10:00:00",
    }
    
    result = await webhook_tool.send_webhook(
        url="https://example.com/webhooks/events",
        data=data
    )
    print(f"Webhook Result: {result}")


# Example 2: Using the Data Transformation Tool
async def example_data_transformation():
    """Example using the Data Transformation Tool."""
    transform_tool = custom_tools_repo.get_tool("data_transformation")
    
    # CSV to JSON
    csv_data = """name,email,age
John Doe,john@example.com,30
Jane Smith,jane@example.com,28"""
    
    json_data = await transform_tool.transform_csv_to_json(csv_data)
    print(f"JSON Data: {json_data}")
    
    # JSON to CSV
    csv_output = await transform_tool.transform_json_to_csv(json_data)
    print(f"CSV Output: {csv_output}")


# Example 3: Using the File Processing Tool
async def example_file_processing():
    """Example using the File Processing Tool."""
    file_tool = custom_tools_repo.get_tool("file_processing")
    
    # Get file metadata
    metadata = await file_tool.get_file_metadata("./data/document.txt")
    print(f"File Metadata: {metadata}")
    
    # Extract text
    content = await file_tool.extract_text_from_file("./data/document.txt")
    print(f"File Content: {content}")


# Example 4: Using the Scheduling Tool
async def example_scheduling_tool():
    """Example using the Scheduling Tool."""
    scheduling_tool = custom_tools_repo.get_tool("scheduling")
    
    # Schedule a task
    success = await scheduling_tool.schedule_task(
        task_name="send_daily_report",
        execution_time="09:00:00",
        payload={"report_type": "daily", "recipients": ["admin@example.com"]}
    )
    
    # Get scheduled tasks
    tasks = await scheduling_tool.get_scheduled_tasks()
    print(f"Scheduled Tasks: {tasks}")


# Example 5: Using the Analytics Tool
async def example_analytics_tool():
    """Example using the Analytics Tool."""
    analytics_tool = custom_tools_repo.get_tool("analytics")
    
    # Track events
    await analytics_tool.track_event(
        event_name="button_clicked",
        properties={"button_id": "submit_btn", "page": "checkout"},
        user_id="user_123"
    )
    
    # Get analytics summary
    summary = await analytics_tool.get_analytics_summary()
    print(f"Analytics Summary: {summary}")


# ============================================================================
# 3. CREATING CUSTOM AGENTS
# ============================================================================

class MyCustomAgent:
    """Example of creating a custom agent."""
    
    def __init__(self):
        """Initialize custom agent."""
        self.name = "MyCustomAgent"
        self.description = "My custom agent for specific tasks"
    
    async def process(self, input_data: str) -> str:
        """Process input and return output."""
        # Your custom logic here
        return f"Processed: {input_data}"


# Register the custom agent
def register_my_agent():
    """Register the custom agent."""
    my_agent = MyCustomAgent()
    custom_registry.register_agent("my_custom_agent", my_agent)
    print("Custom agent registered!")


# Use the custom agent
async def use_my_agent():
    """Use the custom agent."""
    my_agent = custom_registry.get_agent("my_custom_agent")
    result = await my_agent.process("some input")
    print(f"Result: {result}")


# ============================================================================
# 4. CREATING CUSTOM TOOLS
# ============================================================================

class MyCustomTool:
    """Example of creating a custom tool."""
    
    def __init__(self):
        """Initialize custom tool."""
        self.name = "MyCustomTool"
    
    async def do_something(self, param: str) -> dict:
        """Do something useful."""
        return {
            "status": "success",
            "message": f"Did something with {param}"
        }


# Register the custom tool
def register_my_tool():
    """Register the custom tool."""
    my_tool = MyCustomTool()
    custom_tools_repo.register_tool("my_custom_tool", my_tool)
    print("Custom tool registered!")


# Use the custom tool
async def use_my_tool():
    """Use the custom tool."""
    my_tool = custom_tools_repo.get_tool("my_custom_tool")
    result = await my_tool.do_something("test")
    print(f"Result: {result}")


# ============================================================================
# 5. INTEGRATING WITH ORCHESTRATOR
# ============================================================================

from src.ai.orchestrator import AgentOrchestrator

async def integrate_with_orchestrator():
    """Example of integrating custom agents with orchestrator."""
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # List available agents
    agents = custom_registry.list_agents()
    print(f"Available Agents: {agents}")
    
    # List available tools
    tools = custom_tools_repo.list_tools()
    print(f"Available Tools: {tools}")


# ============================================================================
# 6. WORKFLOW EXAMPLE
# ============================================================================

async def complete_workflow_example():
    """Example complete workflow using multiple agents and tools."""
    
    # Step 1: Get analysis
    analysis_agent = custom_registry.get_agent("analysis")
    data = [{"value": 100}, {"value": 200}, {"value": 300}]
    analysis = await analysis_agent.analyze(data)
    print(f"1. Analysis: {analysis}")
    
    # Step 2: Transform data
    transform_tool = custom_tools_repo.get_tool("data_transformation")
    json_data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    csv_output = await transform_tool.transform_json_to_csv(json_data)
    print(f"2. CSV Output: {csv_output}")
    
    # Step 3: Track event
    analytics_tool = custom_tools_repo.get_tool("analytics")
    await analytics_tool.track_event(
        event_name="workflow_completed",
        properties={"duration": "2 seconds"},
        user_id="user_123"
    )
    print("3. Event tracked")
    
    # Step 4: Send webhook
    webhook_tool = custom_tools_repo.get_tool("webhook")
    result = await webhook_tool.send_webhook(
        url="https://example.com/webhooks/workflow_complete",
        data={"status": "success", "timestamp": "2026-05-31T10:00:00"}
    )
    print(f"4. Webhook Result: {result}")


# ============================================================================
# 7. RUNNING EXAMPLES
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def main():
        """Run all examples."""
        print("🚀 Running Custom Agents and Tools Examples")
        print("=" * 50)
        
        try:
            print("\n📋 Example 1: Summary Agent")
            await example_summary_agent()
            
            print("\n📋 Example 2: Analysis Agent")
            await example_analysis_agent()
            
            print("\n📋 Example 3: Recommendation Agent")
            await example_recommendation_agent()
            
            print("\n📋 Example 4: Webhook Tool")
            await example_webhook_tool()
            
            print("\n📋 Example 5: Complete Workflow")
            await complete_workflow_example()
            
            print("\n✅ All examples completed!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    asyncio.run(main())
