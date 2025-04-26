import operator
from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from .config import settings # ใช้ relative import
from .checkpointer import PostgresCheckpointSaver # ใช้ relative import
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

def create_agent_node(llm_model: ChatGoogleGenerativeAI):
    def agent_node(state: AgentState) -> dict:
        logger.debug(f"Agent node received state: {state['messages'][-1].content}")
        try:
            if not settings.google_api_key or settings.google_api_key == "YOUR_GOOGLE_API_KEY":
                 raise ValueError("GOOGLE_API_KEY is not configured.")
            response = llm_model.invoke(state["messages"])
            logger.debug(f"LLM response received: {response.content}")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error invoking LLM: {e}")
            error_message = AIMessage(content=f"Sorry, I encountered an error: {e}")
            return {"messages": [error_message]}
    return agent_node

try:
    if not settings.google_api_key or settings.google_api_key == "YOUR_GOOGLE_API_KEY":
        logger.error("GOOGLE_API_KEY not set. Agent cannot function.")
        llm = None
    else:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=settings.google_api_key)
        logger.info("ChatGoogleGenerativeAI initialized.")

    checkpointer = PostgresCheckpointSaver()
    logger.info("PostgresCheckpointSaver initialized.")

    if llm:
        gemini_agent_node = create_agent_node(llm)
    else:
        def fallback_node(state: AgentState) -> dict:
            logger.warning("LLM not available. Returning fallback message.")
            fallback_msg = AIMessage(content="I cannot process your request right now. Please check the server configuration.")
            return {"messages": [fallback_msg]}
        gemini_agent_node = fallback_node

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", gemini_agent_node)
    graph_builder.set_entry_point("agent")
    graph_builder.add_edge("agent", END)

    agent_executor = graph_builder.compile(checkpointer=checkpointer)
    logger.info("LangGraph agent compiled successfully with checkpointer.")

except Exception as e:
    logger.exception(f"Failed to initialize agent components: {e}")
    agent_executor = None

def get_agent_executor():
    if agent_executor is None:
        raise RuntimeError("Agent executor failed to initialize. Check logs.")
    return agent_executor 