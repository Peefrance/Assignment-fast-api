from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from typing import List
import uuid


logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)


app = FastAPI()


class User(BaseModel):
    first_name: str
    last_name: str
    age: int
    email: EmailStr
    height: float


users_db: List[dict] = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestTimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Request to {request.url} took {process_time:.4f} seconds")
        return response


app.add_middleware(RequestTimerMiddleware)


@app.post("/create-user", status_code=201, response_model=User)
async def create_user(user: User):
    try:
        
        if any(existing_user["email"] == user.email for existing_user in users_db):
            raise HTTPException(status_code=400, detail="Email already exists")

        
        user_id = str(uuid.uuid4())
        users_db.append({"id": user_id, **user.dict()})
        return {"message": "User created successfully", "user_id": user_id, "user": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
