from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysupersecretkey_123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Security scheme for FastAPI
security = HTTPBearer()

class AuthService:
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Check if password matches hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Create password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(username: str, user_id: int) -> str:
        """Create JWT token for user"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": username, "user_id": user_id, "exp": expire}
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        print(f"🔍 DEBUG: Created token for user {username} (ID: {user_id})")
        print(f"🔍 DEBUG: Token expires at: {expire}")
        print(f"🔍 DEBUG: Token: {token[:30]}...")
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Check if JWT token is valid and return payload"""
        print(f"🔍 DEBUG: Verifying token: {token[:20]}...")
        print(f"🔍 DEBUG: SECRET_KEY: {SECRET_KEY[:10]}...")
        print(f"🔍 DEBUG: ALGORITHM: {ALGORITHM}")
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"🔍 DEBUG: Decoded payload: {payload}")
            
            username = payload.get("sub")
            user_id = payload.get("user_id")
            print(f"🔍 DEBUG: Extracted - username: {username}, user_id: {user_id}")
            
            if username is None or user_id is None:
                print("❌ DEBUG: Missing username or user_id in token")
                return None
            
            return {"username": username, "user_id": user_id}
        except JWTError as e:
            print(f"❌ DEBUG: JWT Error: {type(e).__name__}: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ DEBUG: Unexpected error: {type(e).__name__}: {str(e)}")
            return None
    
    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """FastAPI dependency to get current user from token"""
        print(f"🔍 DEBUG: Received credentials: {credentials}")
        print(f"🔍 DEBUG: Token: {credentials.credentials[:20]}..." if credentials.credentials else "No token")
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Add more debugging
            print(f"🔍 DEBUG: About to verify token...")
            payload = AuthService.verify_token(credentials.credentials)
            print(f"🔍 DEBUG: Token verification result: {payload}")
            
            if payload is None:
                print("❌ DEBUG: Payload is None - token verification failed")
                raise credentials_exception
            
            print(f"✅ DEBUG: Authentication successful for user: {payload}")
            return payload
        except Exception as e:
            print(f"❌ DEBUG: Exception during auth: {type(e).__name__}: {str(e)}")
            raise credentials_exception
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Check if user exists and password is correct"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_user(db: Session, email: str, username: str, password: str,
                   full_name: str = None, role: str = "student") -> User:
        """Create a new user account"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            raise ValueError("User already exists")
        
        # Create new user
        hashed_password = AuthService.get_password_hash(password)
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user