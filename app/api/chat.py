import uuid
from fastapi import APIRouter, HTTPException, Path, Body
from app.core.models import ChatMessageRequest, ChatMessageResponse # แก้ import
from app.services import chat_service # แก้ import
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat/{thread_id}", response_model=ChatMessageResponse)
async def chat_endpoint(
    thread_id: str = Path(..., description="The unique identifier for the chat thread/session."),
    request: ChatMessageRequest = Body(...)
):
    """
    Handles chat messages for a given thread, creating a new thread if requested.
    
    Validates the incoming message and thread ID, processes the message using the chat service, and returns the service's reply along with the thread ID. Raises a 400 error for empty messages or invalid thread IDs, and a 500 error for unexpected internal errors.
    
    Args:
        thread_id: The unique identifier for the chat thread or 'new' to start a new thread.
        request: The chat message request payload.
    
    Returns:
        A ChatMessageResponse containing the reply and the thread ID.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    is_new_thread = False
    if thread_id.lower() == "new":
        thread_id = str(uuid.uuid4())
        is_new_thread = True
        logger.info(f"Received 'new' thread request. Generated new thread_id: {thread_id}")
    else:
        try:
            uuid.UUID(thread_id)
        except ValueError:
             raise HTTPException(status_code=400, detail="Invalid thread_id format. Use 'new' or a valid UUID.")
        logger.info(f"Continuing chat for thread_id: {thread_id}")

    try:
        reply = await chat_service.process_message(
            thread_id=thread_id,
            user_message=request.message,
            platform=request.platform,
            user_id=request.user_id,
            project_id=request.project_id
        )
        return ChatMessageResponse(reply=reply, thread_id=thread_id)
    except Exception as e:
        logger.exception(f"Unhandled exception in chat endpoint for thread_id {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 
        print("Triggering CodeRabbit review!")

