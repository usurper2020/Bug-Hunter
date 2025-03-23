from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


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

        @self.app.get("/protected")
        async def protected_route():
            return {"message": "You have access to protected content"}

    def get_app(self):
        """Get the FastAPI application instance"""
        return self.app
        """Get the FastAPI application instance"""
        return self.app
