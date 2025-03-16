from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import timedelta
import logging
from app.auth.auth_manager import AuthManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize authentication
auth_manager = AuthManager()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class APIManager:
    def __init__(self):
        self.app = FastAPI()
        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        """Configure CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Setup API routes"""
        @self.app.post("/token")
        async def login(form_data: OAuth2PasswordRequestForm = Depends()):
            user = auth_manager.authenticate_user(form_data.username, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token = auth_manager.create_access_token(
                data={"sub": user.username}
            )
            return {"access_token": access_token, "token_type": "bearer"}

        @self.app.get("/protected")
        async def protected_route(token: str = Depends(oauth2_scheme)):
            payload = auth_manager.decode_token(token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return {"message": "You have access to protected content"}

    def get_app(self):
        """Get the FastAPI application instance"""
        return self.app
