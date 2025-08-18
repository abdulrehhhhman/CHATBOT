from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import uvicorn
from api.routes import auth, chat
from api.routes import courses

# Fixed imports - remove 'app.' prefix since we're inside app folder
from api.routes import auth, chat
from database.config import get_db, test_db_connection

# Load environment variables
load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "LMS Chatbot API"),
    description="AI-powered educational chatbot with RAG capabilities using Gemini",
    version="1.0.0",
    debug=os.getenv("APP_DEBUG", "True").lower() == "true"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(courses.router)

@app.get("/")
async def root():
    return {
        "message": "LMS Chatbot API is running!",
        "app": os.getenv("APP_NAME"),
        "environment": os.getenv("APP_ENV"),
        "version": "1.0.0",
        "available_endpoints": [
            "/auth/register - Register new user",
            "/auth/login - User login",
            "/chat/message - Send message to AI",
            "/chat/history/{user_id} - Get chat history",
            "/chat/test - Test chat service"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": os.getenv("APP_ENV")}

@app.get("/test-database")
async def test_database():
    """Test database connection"""
    return test_db_connection()

@app.get("/test-gemini")
async def test_gemini():
    """Test Gemini AI connection"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello in one word")
        
        return {
            "status": "success",
            "message": "Gemini API connected successfully",
            "test_response": response.text
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gemini API connection failed: {str(e)}"
        }
# Test Pinecone connection endpoint
# Test Pinecone connection endpoint
@app.get("/test-pinecone")
# Test Pinecone connection endpoint
@app.get("/test-pinecone")
async def test_pinecone():
    try:
        from pinecone import Pinecone, ServerlessSpec
        
        # Initialize Pinecone with new API
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # List existing indexes
        indexes = pc.list_indexes()
        index_names = [index['name'] for index in indexes['indexes']] if indexes and 'indexes' in indexes else []
        
        return {
            "status": "success",
            "message": "Pinecone API connected successfully",
            "indexes": index_names,
            "index_count": len(index_names)
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Pinecone API connection failed: {str(e)}"
        }  

if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)