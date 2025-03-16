import logging
from fastapi import FastAPI
from app.config import settings
from app.db.database_manager import DatabaseManager
from app.db.init_db import initialize_databases
from app.auth.auth_manager import AuthManager
from app.api.api_manager import APIManager
from app.notifications.notification_manager import NotificationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    # Initialize database with configured settings
    db_manager = DatabaseManager(
        sqlite_path=settings.SQLITE_PATH,
        pg_config={
            'dbname': settings.POSTGRES_DB,
            'user': settings.POSTGRES_USER,
            'password': settings.POSTGRES_PASSWORD,
            'host': settings.POSTGRES_HOST,
            'port': settings.POSTGRES_PORT
        }
    )
    initialize_databases()

    # Initialize authentication with configured settings
    auth_manager = AuthManager()

    # Initialize notification system with configured settings
    notification_manager = NotificationManager(db_manager)

    # Initialize API
    api_manager = APIManager()
    app = api_manager.get_app()

    # Add middleware and routes
    @app.on_event("startup")
    async def startup_event():
        logger.info("Application startup - verifying database connection")
        db_manager._initialize_connections()

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Application shutdown - closing database connections")
        db_manager.close()

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.API_HOST, 
        port=settings.API_PORT
    )
