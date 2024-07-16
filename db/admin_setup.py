from sqlalchemy.exc import SQLAlchemyError
from .db_manager.sync_db_manager import SyncDBManager  # Assuming you have SyncDBManager for synchronous operations
from .classDefinitions.user import User
from models.utils_jwt import get_password_hash
from loguru import logger
from constants import user_constants as constants

def create_admin_user():
    sync_db_manager = SyncDBManager()
    session = sync_db_manager.session
    admin_username = "admin"
    admin_password = constants.DEFAULT_PASSWORD  # Change this to a secure password
    admin_email = "admin@example.com"
    
    try:
        # Check if admin user already exists
        admin_user = session.query(User).filter(User.name == admin_username).first()
        if admin_user:
            logger.info("Admin user already exists.")
            return

        # Create the admin user
        hashed_password = get_password_hash(admin_password)
        admin_user = User(
            name=admin_username,
            email=admin_email,
            role=constants.ADMIN_USER_ROLES,  # Assuming 1 is the admin role
            password=hashed_password,
        )
        session.add(admin_user)
        session.commit()
        logger.info("Admin user created successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating admin user: {e}")
    finally:
        session.close()