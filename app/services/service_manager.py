from app.services.scan_service import ScanService
from app.services.auth_service import AuthService
from app.services.database_service import DatabaseService

class ServiceManager:

def __init__(self):
self.database_service = DatabaseService()
self.auth_service = AuthService()
self.scan_service = ScanService()

def get_database_service(self):
return self.database_service

def get_auth_service(self):
return self.auth_service

def get_scan_service(self):
return self.scan_service

def initialize_services(self):
pass
# Initialize any services if needed
self.database_service.initialize()
self.auth_service.initialize()
self.scan_service.initialize()

# Example usage
if __name__ == "__main__":
pass

manager = ServiceManager()
manager.initialize_services()
