"""AI Agent framework using LangGraph."""

import json
import logging
from typing import Any, Optional

# Try to import Google AI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

# Try to import LangChain (optional)
try:
    from langchain.chat_models import ChatGoogle
except ImportError:
    ChatGoogle = None

from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Google AI
if GENAI_AVAILABLE and settings.google_api_key:
    try:
        genai.configure(api_key=settings.google_api_key)
    except Exception as e:
        logger.warning(f"Failed to configure Google AI: {e}")


class AgentState:
    """State for agent processing."""

    def __init__(self, user_id: str, input_text: str):
        """Initialize agent state."""
        self.user_id = user_id
        self.input_text = input_text
        self.output = ""
        self.thoughts = []
        self.actions = []
        self.memories = []


class ChatAgent:
    """Chat agent for conversations using Google AI."""

    def __init__(self, system_prompt: Optional[str] = None):
        """Initialize chat agent with Google AI."""
        if not GENAI_AVAILABLE:
            raise ValueError("google.generativeai package not available")
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured in .env")
        
        self.model = genai.GenerativeModel(settings.google_model)
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.conversation_history = []

    def _get_default_system_prompt(self) -> str:
        """Get customizable system prompt."""
        return """You are an intelligent AI assistant built with Google AI.
Your characteristics:
- Helpful, respectful, and concise
- Ask clarifying questions when uncertain
- Provide accurate information
- Keep responses friendly and engaging
- Use markdown formatting for better readability
- Be professional yet approachable"""

    async def process(self, state: AgentState, custom_prompt: Optional[str] = None) -> str:
        """Process user input and generate response using Google AI."""
        system_prompt = custom_prompt or self.system_prompt
        full_prompt = f"{system_prompt}\n\nUser: {state.input_text}"
        
        try:
            response = self.model.generate_content(full_prompt)
            output = response.text
            state.output = output
            return output
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I encountered an error processing your request. Please try again."


class ResearchAgent:
    """Research agent for knowledge base search."""

    async def process(self, state: AgentState) -> str:
        """Search knowledge base for relevant information."""
        logger.info(f"Research agent processing: {state.input_text}")
        return f"Searching knowledge base for: {state.input_text}"


class MemoryAgent:
    """Memory agent for storing and retrieving memories."""

    async def process(self, state: AgentState) -> str:
        """Store or retrieve memories."""
        logger.info(f"Memory agent processing: {state.input_text}")
        return "Memory operation completed"


class WorkflowAgent:
    """Workflow agent for task automation."""

    async def process(self, state: AgentState) -> str:
        """Execute workflow tasks."""
        logger.info(f"Workflow agent processing: {state.input_text}")
        return "Workflow execution completed"


class PlannerAgent:
    """Planner agent for breaking down complex requests."""

    async def process(self, state: AgentState) -> str:
        """Break down complex requests into steps."""
        logger.info(f"Planner agent processing: {state.input_text}")
        return "Plan created for: " + state.input_text


class ToolAgent:
    """Tool agent for using external APIs."""

    async def process(self, state: AgentState) -> str:
        """Execute external tool calls."""
        logger.info(f"Tool agent processing: {state.input_text}")
        return "Tool execution completed"


class AgentOrchestrator:
    """Orchestrator for managing multiple agents."""

    def __init__(self, custom_prompts: Optional[dict] = None):
        """Initialize orchestrator."""
        try:
            custom_chat_prompt = custom_prompts.get("chat") if custom_prompts else None
            self.chat_agent = ChatAgent(system_prompt=custom_chat_prompt)
        except ValueError as e:
            logger.error(f"Failed to initialize ChatAgent: {e}")
            raise
        
        self.research_agent = ResearchAgent()
        self.memory_agent = MemoryAgent()
        self.workflow_agent = WorkflowAgent()
        self.planner_agent = PlannerAgent()
        self.tool_agent = ToolAgent()
        
        # Track agent usage and performance
        self.usage_stats = {
            "chat": 0,
            "research": 0,
            "memory": 0,
            "workflow": 0,
            "planner": 0,
            "tool": 0,
        }
        
        self.custom_prompts = custom_prompts or {}

    def get_agent_for_input(self, input_text: str) -> tuple[str, Any]:
        """Determine which agent to use based on input analysis."""
        input_lower = input_text.lower()
        
        # Priority-based routing
        if any(keyword in input_lower for keyword in ["remember", "memory", "forget", "recall"]):
            return "memory", self.memory_agent
        elif any(keyword in input_lower for keyword in ["search", "find", "lookup", "research"]):
            return "research", self.research_agent
        elif any(keyword in input_lower for keyword in ["plan", "schedule", "break down", "steps"]):
            return "planner", self.planner_agent
        elif any(keyword in input_lower for keyword in ["workflow", "automate", "task", "execute"]):
            return "workflow", self.workflow_agent
        elif any(keyword in input_lower for keyword in ["calculate", "api", "tool", "function"]):
            return "tool", self.tool_agent
        else:
            return "chat", self.chat_agent

    async def process(self, user_id: str, input_text: str, custom_prompt: Optional[str] = None) -> str:
        """Process user input through agent system."""
        state = AgentState(user_id, input_text)
        
        logger.info(f"Processing message from {user_id}: {input_text[:50]}...")
        
        # Determine agent
        agent_name, agent = self.get_agent_for_input(input_text)
        
        # Track usage
        self.usage_stats[agent_name] += 1
        
        # Route to appropriate agent
        if agent_name == "chat":
            response = await agent.process(state, custom_prompt)
        else:
            response = await agent.process(state)
        
        logger.info(f"Generated response via {agent_name} agent for {user_id}")
        return response

    def get_usage_stats(self) -> dict:
        """Get agent usage statistics."""
        return self.usage_stats.copy()

    def set_custom_prompt(self, agent_type: str, prompt: str) -> None:
        """Set custom prompt for an agent."""
        if agent_type == "chat":
            self.chat_agent.system_prompt = prompt
            logger.info(f"Updated custom prompt for {agent_type} agent")
        else:
            logger.warning(f"Custom prompts not supported for {agent_type} agent")


# Global orchestrator instance (lazy-loaded)
_agent_orchestrator = None


def get_agent_orchestrator() -> Optional[AgentOrchestrator]:
    """Get or create the global orchestrator instance."""
    global _agent_orchestrator
    if _agent_orchestrator is None:
        try:
            _agent_orchestrator = AgentOrchestrator()
        except ValueError as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            return None
    return _agent_orchestrator


# For backwards compatibility
agent_orchestrator = None
