from pydantic import BaseModel

class ChatMessageRequest(BaseModel):
    message: str
    platform: str = "web"
    user_id: str = "default_user"
    project_id: str = "default_project"

class ChatMessageResponse(BaseModel):
    reply: str
    thread_id: str 