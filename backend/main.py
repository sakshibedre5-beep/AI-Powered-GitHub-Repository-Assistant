from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext


from database.connection import engine, Base, SessionLocal
from models.user import User
from schemas.user import UserCreate, UserLogin
from auth import create_access_token
from schemas.repository import RepositoryImport
from services.github_service import (
    get_repository_info,
    get_repository_files,
    get_file_content
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "CodeLens Backend is running!"
    }


@app.get("/db-test")
def database_test():
    with engine.connect():
        return {
            "message": "Database connected successfully!"
        }


@app.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }


@app.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = pwd_context.verify(
        user.password,
        existing_user.password
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": str(existing_user.id),
            "email": existing_user.email
        }
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/repositories/import")
def import_repository(repository: RepositoryImport):

    try:
        repo_info = get_repository_info(
            str(repository.repo_url)
        )

        return {
            "message": "Repository imported successfully",
            "repository": repo_info
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
@app.get("/repositories/files/{owner}/{repo}")
def repository_files(owner: str, repo: str):

    try:
        files = get_repository_files(owner, repo)

        return {
            "owner": owner,
            "repository": repo,
            "files": files
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
@app.get("/repositories/file")
def repository_file(
    owner: str,
    repo: str,
    path: str
):

    try:
        file_data = get_file_content(
            owner,
            repo,
            path
        )

        return file_data

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )