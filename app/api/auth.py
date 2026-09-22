from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.user import authenticate_user, create_user, create_user_access_token
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="register User")
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    return create_user(
        db=db,
        username=payload.username,
        email=str(payload.email),
        password=payload.password
    )


@router.post("/login", response_model=TokenResponse, summary="login user")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db=db, email=str(
        payload.email), password=payload.password)
    token = create_user_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
    }
