from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database.config import get_db
from services.rag import RAGService
from services.auth import AuthService
import uuid

router = APIRouter(prefix="/courses", tags=["Courses"])

# Initialize services (delayed for RAG)
rag_service = None

def get_rag_service():
    """Get RAG service instance (lazy loading)"""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service

# Pydantic models
class QuestionRequest(BaseModel):
    question: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    upload_date: str
    file_size: int
    total_chunks: int
    status: str

class QuestionResponse(BaseModel):
    answer: str
    sources: List[dict]
    has_context: bool
    chunks_used: Optional[int] = None

# Dependency to get current user ID
async def get_current_user_id(current_user: dict = Depends(AuthService.get_current_user)) -> int:
    """Extract user ID from token"""
    return current_user["user_id"]

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Upload and process a course document (PDF)"""
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Check file size (max 10MB)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB"
        )
    
    if len(file_content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded"
        )
    
    try:
        rag = get_rag_service()
        result = await rag.upload_document(
            file_content=file_content,
            filename=file.filename,
            user_id=current_user_id,
            db=db
        )
        
        if result["success"]:
            return {
                "message": result["message"],
                "course_id": result["course_id"],
                "chunks_created": result["chunks_created"],
                "filename": file.filename
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    question_data: QuestionRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """Ask a question about uploaded course materials"""
    if not question_data.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    try:
        rag = get_rag_service()
        result = await rag.answer_question(
            question=question_data.question,
            user_id=current_user_id
        )
        
        return QuestionResponse(
            answer=result["answer"],
            sources=result["sources"],
            has_context=result["has_context"],
            chunks_used=result.get("chunks_used")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error answering question: {str(e)}"
        )

@router.get("/documents", response_model=List[DocumentResponse])
async def get_user_documents(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get list of user's uploaded documents"""
    try:
        rag = get_rag_service()
        documents = rag.get_user_documents(current_user_id, db)
        
        return [
            DocumentResponse(
                id=doc["id"],
                filename=doc["filename"],
                upload_date=doc["upload_date"].isoformat() if hasattr(doc["upload_date"], 'isoformat') else str(doc["upload_date"]),
                file_size=doc["file_size"],
                total_chunks=doc["total_chunks"],
                status=doc["status"]
            ) for doc in documents
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        )

@router.get("/search")
async def search_documents(
    query: str,
    top_k: int = 3,
    current_user_id: int = Depends(get_current_user_id)
):
    """Search through uploaded documents"""
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )
    
    try:
        rag = get_rag_service()
        results = rag.search_documents(
            query=query,
            user_id=current_user_id,
            top_k=min(top_k, 10)  # Limit to max 10 results
        )
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching documents: {str(e)}"
        )

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Delete a document (this is a placeholder - you'd need to implement Pinecone deletion)"""
    # For now, just delete from database
    # TODO: Also delete from Pinecone index
    try:
        from models.course import Course
        course = db.query(Course).filter(
            Course.id == document_id,
            Course.user_id == current_user_id
        ).first()
        
        if not course:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        db.delete(course)
        db.commit()
        
        return {
            "message": f"Document '{course.filename}' deleted successfully",
            "deleted_document_id": document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )