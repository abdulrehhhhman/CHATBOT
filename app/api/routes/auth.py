from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.config import get_db
from services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Request models
class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: str = None
    role: str = "student"

class UserLogin(BaseModel):
    email: str
    password: str

# Response models
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str = None
    role: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = AuthService.create_user(
            db=db,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role
        )
        
        return {
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role
            }
        }
    except ValueError as e:
        print(f"ValueError in registration: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception in registration: {str(e)}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.post("/login")
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = AuthService.authenticate_user(db, user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account disabled")
    
    # Create access token with user_id
    access_token = AuthService.create_access_token(user.username, user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.get("/me")
def get_current_user_info(
    current_user: dict = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user info"""
    try:
        from models.user import User
        user = db.query(User).filter(User.id == current_user["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user info")