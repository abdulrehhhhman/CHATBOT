import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class GeminiService:
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_educational_response(self, user_question: str, context: str = None) -> str:
        """Generate educational response using Gemini"""
        try:
            # Create educational prompt
            system_prompt = """You are an AI tutor for a Learning Management System. 
            Your role is to:
            - Answer student questions clearly and educational manner
            - Explain concepts step by step
            - Provide examples when helpful
            - Be encouraging and supportive
            - Keep responses focused and not too long
            
            If you don't know something, say so honestly and suggest where to find the answer.
            """
            
            if context:
                prompt = f"{system_prompt}\n\nContext: {context}\n\nStudent Question: {user_question}"
            else:
                prompt = f"{system_prompt}\n\nStudent Question: {user_question}"
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"I'm having trouble generating a response right now. Error: {str(e)}"
    
    def generate_simple_response(self, message: str) -> str:
        """Generate a simple response for basic chat"""
        try:
            response = self.model.generate_content(f"Answer this educational question: {message}")
            return response.text
        except Exception as e:
            return f"Sorry, I'm having technical difficulties. Please try again later."
    
    def test_connection(self) -> dict:
        """Test if Gemini API is working"""
        try:
            response = self.model.generate_content("Say hello in one word")
            return {
                "status": "success",
                "message": "Gemini connected successfully",
                "test_response": response.text
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Gemini connection failed: {str(e)}"
            }