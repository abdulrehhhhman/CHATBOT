import os
import uuid
from typing import List, Optional
from datetime import datetime
import PyPDF2
from io import BytesIO

# Pinecone imports
from pinecone import Pinecone, ServerlessSpec

# Google AI imports
import google.generativeai as genai

# Database imports
from sqlalchemy.orm import Session
from models.course import Course
from models.user import User

# Environment
from dotenv import load_dotenv
load_dotenv()

class RAGService:
    def __init__(self):
        """Initialize RAG service with Pinecone and Gemini"""
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "lms-chatbot-index")
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize index (will be set later)
        self.index = None
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        
        # Get the index only if it exists
        try:
            self.index = self.pc.Index(self.index_name)
            print(f"✅ Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            print(f"Warning: Could not connect to index {self.index_name}: {str(e)}")
            print("RAG functionality will be limited until index is created.")
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        try:
            # Fix: Updated API call for newer Pinecone versions
            existing_indexes = self.pc.list_indexes()
            
            # Handle different response formats
            if hasattr(existing_indexes, 'names'):
                # Newer API format
                index_names = existing_indexes.names()
            elif isinstance(existing_indexes, dict) and 'indexes' in existing_indexes:
                # Older API format with dict
                index_names = [idx['name'] for idx in existing_indexes['indexes']]
            elif isinstance(existing_indexes, list):
                # Simple list format
                index_names = [idx.get('name', str(idx)) for idx in existing_indexes]
            else:
                # Fallback: convert to list and extract names
                index_names = []
                try:
                    for idx in existing_indexes:
                        if isinstance(idx, dict):
                            index_names.append(idx.get('name', ''))
                        else:
                            index_names.append(str(idx))
                except:
                    print("Could not parse existing indexes, proceeding to create new index")
                    index_names = []
            
            print(f"Found existing indexes: {index_names}")
            
            if self.index_name not in index_names:
                print(f"Creating new Pinecone index: {self.index_name}")
                
                # Try different cloud providers and regions
                specs_to_try = [
                    {"cloud": "aws", "region": "us-east-1"},
                    {"cloud": "gcp", "region": "us-central1"},
                    {"cloud": "aws", "region": "us-west-2"}
                ]
                
                success = False
                for spec_config in specs_to_try:
                    try:
                        self.pc.create_index(
                            name=self.index_name,
                            dimension=768,
                            metric="cosine",
                            spec=ServerlessSpec(**spec_config)
                        )
                        print(f"✅ Index {self.index_name} created successfully with {spec_config}")
                        success = True
                        break
                    except Exception as create_error:
                        print(f"❌ Failed to create index with {spec_config}: {str(create_error)}")
                        continue
                
                if not success:
                    print("❌ Failed to create index with any configuration")
                    raise Exception("Could not create Pinecone index")
                    
            else:
                print(f"✅ Index {self.index_name} already exists")
                
        except Exception as e:
            print(f"❌ Error ensuring index exists: {str(e)}")
            print("RAG functionality may be limited")
            # Don't raise the exception, allow the service to continue with limited functionality
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            text = ""
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                raise Exception("No readable text found in PDF")
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence or word boundary
            if end < len(text):
                # Look for sentence ending
                sentence_end = text.rfind('.', start, end)
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    space = text.rfind(' ', start, end)
                    if space != -1 and space > start + chunk_size // 2:
                        end = space
            
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for text chunks using Gemini"""
        embeddings = []
        
        for text in texts:
            try:
                # Use Gemini's embedding model
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            except Exception as e:
                print(f"Error getting embedding for text: {str(e)}")
                # Fallback: create a dummy embedding
                embeddings.append([0.0] * 768)
        
        return embeddings
    
    async def upload_document(
        self, 
        file_content: bytes, 
        filename: str, 
        user_id: int, 
        db: Session
    ) -> dict:
        """Upload and process a document"""
        try:
            print(f"🔄 Processing document: {filename}")
            
            # Check if index is available
            if self.index is None:
                raise Exception("Pinecone index not available. Please check your Pinecone configuration.")
            
            # Extract text from PDF
            print("📄 Extracting text from PDF...")
            text_content = self.extract_text_from_pdf(file_content)
            
            if not text_content.strip():
                raise Exception("No text found in the PDF")
            
            print(f"✅ Extracted {len(text_content)} characters")
            
            # Chunk the text
            print("✂️ Chunking text...")
            chunks = self.chunk_text(text_content)
            print(f"✅ Created {len(chunks)} chunks")
            
            # Get embeddings
            print("🔢 Generating embeddings...")
            embeddings = self.get_embeddings(chunks)
            print(f"✅ Generated {len(embeddings)} embeddings")
            
            # Generate unique IDs for chunks
            chunk_ids = [f"doc_{user_id}_{uuid.uuid4()}" for _ in chunks]
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (chunk_id, chunk_text, embedding) in enumerate(zip(chunk_ids, chunks, embeddings)):
                vectors.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": {
                        "text": chunk_text,
                        "filename": filename,
                        "user_id": user_id,
                        "chunk_index": i,
                        "upload_date": datetime.now().isoformat()
                    }
                })
            
            # Upload to Pinecone in batches
            print("☁️ Uploading to Pinecone...")
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            print(f"✅ Uploaded {len(vectors)} vectors to Pinecone")
            
            # Save course info to database - FIX: Use CourseMaterial model instead
            from models.course import CourseMaterial
            
            course_material = CourseMaterial(
                course_id=1,  # Default course for now
                filename=filename,
                original_filename=filename,
                file_path=f"uploads/{filename}",  # Virtual path
                file_type="pdf",
                file_size=len(file_content),
                extracted_text=text_content[:5000],  # Store first 5000 chars
                is_processed=True,
                uploaded_by=user_id,
                uploaded_at=datetime.now(),
                description=f"Processed PDF with {len(chunks)} chunks"
            )
            
            db.add(course_material)
            db.commit()
            db.refresh(course_material)
            
            return {
                "success": True,
                "message": f"Document '{filename}' processed successfully",
                "course_id": course_material.id,
                "chunks_created": len(chunks),
                "text_length": len(text_content)
            }
            
        except Exception as e:
            print(f"❌ Error processing document: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing document: {str(e)}"
            }
    
    def search_documents(self, query: str, user_id: int, top_k: int = 3) -> List[dict]:
        """Search for relevant document chunks"""
        try:
            if self.index is None:
                print("❌ Pinecone index not available")
                return []
            
            # Get query embedding
            query_embedding = self.get_embeddings([query])[0]
            
            # Search in Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                filter={"user_id": {"$eq": user_id}},
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract relevant information
            relevant_chunks = []
            for match in search_results['matches']:
                relevant_chunks.append({
                    "text": match['metadata']['text'],
                    "filename": match['metadata']['filename'],
                    "score": match['score'],
                    "chunk_index": match['metadata']['chunk_index']
                })
            
            return relevant_chunks
            
        except Exception as e:
            print(f"❌ Error searching documents: {str(e)}")
            return []
    
    async def answer_question(self, question: str, user_id: int) -> dict:
        """Answer question using RAG"""
        try:
            # Search for relevant documents
            relevant_chunks = self.search_documents(question, user_id)
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find any relevant information in your uploaded documents. Please make sure you've uploaded course materials related to your question.",
                    "sources": [],
                    "has_context": False
                }
            
            # Prepare context
            context = "\n\n".join([
                f"From {chunk['filename']}:\n{chunk['text']}"
                for chunk in relevant_chunks
            ])
            
            # Create prompt
            prompt = f"""
Based on the following course materials, please answer the student's question comprehensively and accurately.

COURSE MATERIALS:
{context}

STUDENT QUESTION: {question}

INSTRUCTIONS:
- Answer based primarily on the provided course materials
- If the materials don't fully address the question, clearly state what's missing
- Provide examples from the materials when possible
- Keep the answer educational and helpful
- If asked about topics not covered in the materials, suggest what additional resources might be needed

ANSWER:
"""
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            # Prepare sources
            sources = [
                {
                    "filename": chunk['filename'],
                    "relevance_score": chunk['score'],
                    "preview": chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
                }
                for chunk in relevant_chunks
            ]
            
            return {
                "answer": response.text,
                "sources": sources,
                "has_context": True,
                "chunks_used": len(relevant_chunks)
            }
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "has_context": False
            }
    
    def get_user_documents(self, user_id: int, db: Session) -> List[dict]:
        """Get list of user's uploaded documents"""
        try:
            from models.course import CourseMaterial
            
            materials = db.query(CourseMaterial).filter(
                CourseMaterial.uploaded_by == user_id
            ).all()
            
            return [
                {
                    "id": material.id,
                    "filename": material.filename,
                    "upload_date": material.uploaded_at,
                    "file_size": material.file_size,
                    "total_chunks": len(material.extracted_text.split()) // 100 if material.extracted_text else 0,  # Rough estimate
                    "status": "processed" if material.is_processed else "pending"
                }
                for material in materials
            ]
            
        except Exception as e:
            print(f"❌ Error getting user documents: {str(e)}")
            return []