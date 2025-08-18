from sqlalchemy.orm import Session
from models.chat import Chat
from models.user import User
from services.gemini import GeminiService
from datetime import datetime
from typing import List, Optional
import uuid

class ChatService:
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def send_message(self, db: Session, user_id: int, message: str, 
                    course_id: Optional[int] = None) -> dict:
        """Process user message and return AI response"""
        try:
            # Get AI response from Gemini
            ai_response = self.gemini_service.generate_educational_response(message)
            
            # Save chat to database
            chat = Chat(
                user_id=user_id,
                user_message=message,
                ai_response=ai_response,
                course_id=course_id,
                context_type="general",
                conversation_id=str(uuid.uuid4())[:8],  # Short conversation ID
                response_time=datetime.utcnow()
            )
            
            db.add(chat)
            db.commit()
            db.refresh(chat)
            
            return {
                "status": "success",
                "chat_id": chat.id,
                "user_message": message,
                "ai_response": ai_response,
                "timestamp": chat.created_at
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process message: {str(e)}"
            }
    
    def get_chat_history(self, db: Session, user_id: int, limit: int = 20) -> List[dict]:
        """Get user's recent chat history"""
        try:
            chats = db.query(Chat).filter(
                Chat.user_id == user_id
            ).order_by(Chat.created_at.desc()).limit(limit).all()
            
            history = []
            for chat in chats:
                history.append({
                    "id": chat.id,
                    "user_message": chat.user_message,
                    "ai_response": chat.ai_response,
                    "timestamp": chat.created_at,
                    "course_id": chat.course_id
                })
            
            return history
            
        except Exception as e:
            return []
    
    def get_conversation(self, db: Session, conversation_id: str) -> List[dict]:
        """Get all messages in a conversation"""
        try:
            chats = db.query(Chat).filter(
                Chat.conversation_id == conversation_id
            ).order_by(Chat.created_at.asc()).all()
            
            conversation = []
            for chat in chats:
                conversation.append({
                    "id": chat.id,
                    "user_message": chat.user_message,
                    "ai_response": chat.ai_response,
                    "timestamp": chat.created_at
                })
            
            return conversation
            
        except Exception as e:
            return []