from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(String(100), nullable=True)  # Group messages in conversations
    
    # Message content
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    
    # Context information
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)  # If related to specific course
    context_type = Column(String(50), default="general")  # general, course_specific, rag
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    response_time = Column(DateTime(timezone=True), nullable=True)  # When AI responded
    
    # Status
    is_resolved = Column(Boolean, default=False)
    rating = Column(Integer, nullable=True)  # User can rate AI response (1-5)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    course = relationship("Course", back_populates="chats")
    
    def __repr__(self):
        return f"<Chat(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"