from app.core.agent import get_agent_executor # แก้ import
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from typing import List
import logging

logger = logging.getLogger(__name__)

async def process_message(
    thread_id: str,
    user_message: str,
    platform: str = "web",
    user_id: str = "default_user",
    project_id: str = "default_project"
) -> str:
    logger.info(f"Processing message for thread_id: {thread_id}, platform: {platform}, user_id: {user_id}, project_id: {project_id}")
    try:
        agent_executor = get_agent_executor()
        config = {
            "configurable": {
                "thread_id": thread_id,
                "platform": platform,
                "user_id": user_id,
                "project_id": project_id,
            }
        }
        input_message = HumanMessage(content=user_message)
        final_state = await agent_executor.ainvoke({"messages": [input_message]}, config=config)
        ai_response: BaseMessage = final_state["messages"][-1]

        if isinstance(ai_response, AIMessage):
             logger.info(f"Agent response for thread_id {thread_id}: {ai_response.content[:50]}...")
             return ai_response.content
        else:
             logger.warning(f"Last message is not AIMessage for thread_id {thread_id}: {type(ai_response)}")
             last_message_content = getattr(ai_response, 'content', "Agent did not provide a standard text response.")
             return last_message_content if isinstance(last_message_content, str) else "Agent response format unclear."

    except Exception as e:
        logger.exception(f"Error processing message for thread_id {thread_id}: {e}")
        return "Sorry, I encountered an error while processing your request." 