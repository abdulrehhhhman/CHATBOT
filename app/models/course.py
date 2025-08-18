from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    course_code = Column(String(50), unique=True, nullable=False)  # e.g., "CS101"
    
    # Course details
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    semester = Column(String(50), nullable=True)  # "Fall 2024"
    credits = Column(Integer, default=3)
    
    # Status
    is_active = Column(Boolean, default=True)
    enrollment_open = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    instructor = relationship("User", foreign_keys=[instructor_id])
    enrollments = relationship("CourseEnrollment", back_populates="course")
    materials = relationship("CourseMaterial", back_populates="course")
    chats = relationship("Chat", back_populates="course")
    
    def __repr__(self):
        return f"<Course(id={self.id}, code={self.course_code}, title={self.title})>"


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Enrollment details
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="active")  # active, completed, dropped
    grade = Column(String(10), nullable=True)  # A, B, C, etc.
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    def __repr__(self):
        return f"<Enrollment(user_id={self.user_id}, course_id={self.course_id})>"


class CourseMaterial(Base):
    __tablename__ = "course_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # File details
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt
    file_size = Column(Integer, nullable=False)  # in bytes
    
    # Content for RAG
    extracted_text = Column(Text, nullable=True)  # Extracted text content
    is_processed = Column(Boolean, default=False)  # For vector embeddings
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(Text, nullable=True)
    
    # Relationships
    course = relationship("Course", back_populates="materials")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f"<Material(id={self.id}, filename={self.filename}, course_id={self.course_id})>"