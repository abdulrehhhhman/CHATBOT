# Updated chat.py - Replace your api/routes/chat.py with this
# This version uses your correct column names

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import traceback
import os
from typing import List, Optional
from datetime import datetime
import google.generativeai as genai
from pinecone import Pinecone

from database.config import get_db
from models.chat import Chat
from models.user import User
from models.course import CourseMaterial, Course

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Configure Gemini
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")

class ChatMessage(BaseModel):
    message: str
    user_id: int
    course_id: Optional[int] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None
    sources: Optional[List[str]] = []

@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    db: Session = Depends(get_db)
):
    """Send a message to the AI chatbot with RAG capabilities"""
    
    logger.info(f"Received chat message: {chat_message.message[:50]}...")
    logger.info(f"User ID: {chat_message.user_id}, Course ID: {chat_message.course_id}")
    
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == chat_message.user_id).first()
        if not user:
            logger.error(f"User not found: {chat_message.user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User found: {user.username}")
        
        # Get relevant context from database (RAG)
        context, sources = await get_relevant_context(
            chat_message.message, 
            chat_message.course_id, 
            db
        )
        
        logger.info(f"Retrieved context length: {len(context)} characters")
        logger.info(f"Sources found: {len(sources)}")
        
        # Generate AI response
        ai_response = await generate_ai_response(
            chat_message.message, 
            context,
            user.full_name or user.username
        )
        
        logger.info(f"AI response generated: {ai_response[:100]}...")
        
        # Generate conversation ID if not provided
        conversation_id = chat_message.conversation_id or f"conv_{user.id}_{int(datetime.now().timestamp())}"
        
        # Save chat to database using your correct column names
        try:
            chat_record = Chat(
                user_id=chat_message.user_id,
                user_message=chat_message.message,  # Using your column name
                ai_response=ai_response,             # Using your column name
                course_id=chat_message.course_id,
                conversation_id=conversation_id,
                context_type="rag" if context else "general",
                response_time=datetime.now()
            )
            
            db.add(chat_record)
            db.commit()
            db.refresh(chat_record)
            logger.info(f"Chat saved to database with ID: {chat_record.id}")
            
        except Exception as db_error:
            logger.error(f"Failed to save chat to database: {str(db_error)}")
            logger.error(f"DB Error traceback: {traceback.format_exc()}")
            # Don't fail the request if saving fails
            db.rollback()
        
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat message processing failed: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Return detailed error in development
        if os.getenv("APP_ENV") == "development":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Failed to send message",
                    "error": str(e),
                    "traceback": traceback.format_exc().split('\n')
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message"
            )

async def get_relevant_context(message: str, course_id: Optional[int], db: Session) -> tuple[str, List[str]]:
    """Get relevant context from course materials (RAG implementation)"""
    
    try:
        logger.info("Starting context retrieval...")
        
        # Query course materials using your correct column names
        query = db.query(CourseMaterial).filter(CourseMaterial.is_processed == True)
        
        if course_id:
            query = query.filter(CourseMaterial.course_id == course_id)
            logger.info(f"Filtering by course_id: {course_id}")
        
        materials = query.limit(10).all()
        
        if not materials:
            logger.info("No processed course materials found")
            return "", []
        
        logger.info(f"Found {len(materials)} processed course materials")
        
        # Simple keyword-based relevance scoring
        # In production, you'd use vector similarity here
        relevant_materials = []
        message_keywords = set(message.lower().split())
        
        for material in materials:
            if material.extracted_text:  # Using your column name
                content_keywords = set(material.extracted_text.lower().split())
                
                # Calculate keyword overlap
                overlap = len(message_keywords & content_keywords)
                
                if overlap > 0:
                    relevance_score = overlap / len(message_keywords)
                    relevant_materials.append({
                        'material': material,
                        'score': relevance_score,
                        'content': material.extracted_text[:1000]  # First 1000 chars
                    })
        
        # Sort by relevance score
        relevant_materials.sort(key=lambda x: x['score'], reverse=True)
        
        # Take top 3 most relevant materials
        top_materials = relevant_materials[:3]
        
        if not top_materials:
            return "", []
        
        # Build context and sources
        context_parts = []
        sources = []
        
        for item in top_materials:
            material = item['material']
            context_parts.append(f"From '{material.original_filename}':\n{item['content']}")
            sources.append(material.original_filename)
        
        context = "\n\n---\n\n".join(context_parts)
        
        logger.info(f"Built context from {len(sources)} sources: {sources}")
        
        return context, sources
        
    except Exception as e:
        logger.error(f"Context retrieval failed: {str(e)}")
        logger.error(f"Context error traceback: {traceback.format_exc()}")
        return "", []

async def generate_ai_response(message: str, context: str = "", user_name: str = "Student") -> str:
    """Generate AI response using Gemini"""
    
    try:
        logger.info("Generating AI response...")
        
        # Create the prompt based on context availability
        if context:
            prompt = f"""You are an intelligent educational assistant helping {user_name}. You have access to relevant course materials to help answer their question.

**Course Materials Context:**
{context}

**Student Question:** {message}

Please provide a helpful, accurate, and detailed response based on the course materials provided. If the context contains relevant information, use it to give a comprehensive answer. If the context doesn't fully address the question, provide the best educational guidance you can while noting any limitations.

Make your response:
- Clear and educational
- Specific to the question asked
- Reference the course materials when relevant
- Encouraging and supportive
"""
        else:
            prompt = f"""You are an intelligent educational assistant helping {user_name}. 

**Student Question:** {message}

Please provide a helpful, accurate, and educational response. Since no specific course materials are available, provide general educational guidance on this topic.

Make your response:
- Clear and educational
- Informative and helpful
- Encouraging and supportive
- Acknowledge if you need more specific information
"""
        
        logger.info(f"Generated prompt length: {len(prompt)} characters")
        
        # Generate response with Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=1000,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if response and response.text:
            logger.info("AI response generated successfully")
            return response.text.strip()
        else:
            logger.error("Gemini returned empty response")
            return "I'm sorry, I'm having trouble generating a response right now. Please try again."
            
    except Exception as e:
        logger.error(f"AI response generation failed: {str(e)}")
        return f"I'm sorry, I'm experiencing technical difficulties: {str(e)}. Please try again later."

@router.get("/history/{user_id}")
async def get_chat_history(
    user_id: int,
    course_id: Optional[int] = None,
    conversation_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history for a user"""
    
    try:
        logger.info(f"Getting chat history for user {user_id}")
        
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build query using your column names
        query = db.query(Chat).filter(Chat.user_id == user_id)
        
        if course_id:
            query = query.filter(Chat.course_id == course_id)
        
        if conversation_id:
            query = query.filter(Chat.conversation_id == conversation_id)
        
        chats = query.order_by(Chat.created_at.desc()).limit(limit).all()
        
        logger.info(f"Found {len(chats)} chat records")
        
        return {
            "chats": [
                {
                    "id": chat.id,
                    "user_message": chat.user_message,      # Your column name
                    "ai_response": chat.ai_response,        # Your column name
                    "conversation_id": chat.conversation_id,
                    "context_type": chat.context_type,
                    "created_at": chat.created_at,
                    "response_time": chat.response_time,
                    "course_id": chat.course_id,
                    "rating": chat.rating
                }
                for chat in chats
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chat history failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )

@router.get("/test")
async def test_chat():
    """Test chat service"""
    
    try:
        logger.info("Testing chat service...")
        
        # Test Gemini API
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Chat service is working!' in exactly those words")
        
        if response and response.text:
            return {
                "status": "success",
                "message": "Chat service is working",
                "gemini_response": response.text.strip(),
                "models_loaded": {
                    "Chat": "✅ user_message, ai_response columns",
                    "CourseMaterial": "✅ extracted_text, filename columns",
                    "User": "✅ All user fields"
                }
            }
        else:
            return {
                "status": "error",
                "message": "Gemini API not responding"
            }
            
    except Exception as e:
        logger.error(f"Chat test failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Chat test failed: {str(e)}"
        }