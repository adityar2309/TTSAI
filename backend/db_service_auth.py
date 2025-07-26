"""
Database service extensions for authentication
"""
import sqlite3
import json
import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class AuthDBService:
    """
    Database service methods for authentication
    """
    def __init__(self, db_path):
        """Initialize with database path"""
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create user_sessions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                token TEXT,
                created_at TEXT,
                expires_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Auth tables created successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Database error creating auth tables: {e}")
            raise
    
    def get_user_by_google_id(self, google_id):
        """
        Get user by Google ID
        
        Args:
            google_id (str): Google ID
            
        Returns:
            dict: User record or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM users WHERE google_id = ?",
                (google_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user = dict(row)
                return user
            
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Database error getting user by Google ID: {e}")
            return None
    
    def get_user_by_email(self, email):
        """
        Get user by email
        
        Args:
            email (str): User email
            
        Returns:
            dict: User record or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user = dict(row)
                return user
            
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Database error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User record or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user = dict(row)
                return user
            
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Database error getting user by ID: {e}")
            return None
    
    def create_user(self, user_data):
        """
        Create a new user
        
        Args:
            user_data (dict): User data
            
        Returns:
            str: User ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate UUID for user
            user_id = str(uuid.uuid4())
            
            cursor.execute(
                """
                INSERT INTO users (
                    id, google_id, name, email, profile_picture,
                    created_at, updated_at, last_login
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    user_data.get('google_id'),
                    user_data.get('name'),
                    user_data.get('email'),
                    user_data.get('profile_picture'),
                    user_data.get('created_at', datetime.now().isoformat()),
                    user_data.get('updated_at', datetime.now().isoformat()),
                    user_data.get('last_login', datetime.now().isoformat())
                )
            )
            
            conn.commit()
            conn.close()
            
            return user_id
            
        except sqlite3.Error as e:
            logger.error(f"Database error creating user: {e}")
            raise
    
    def update_user(self, user_data):
        """
        Update an existing user
        
        Args:
            user_data (dict): User data with ID
            
        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE users SET
                    name = COALESCE(?, name),
                    email = COALESCE(?, email),
                    profile_picture = COALESCE(?, profile_picture),
                    updated_at = ?,
                    last_login = COALESCE(?, last_login)
                WHERE id = ?
                """,
                (
                    user_data.get('name'),
                    user_data.get('email'),
                    user_data.get('profile_picture'),
                    datetime.now().isoformat(),
                    user_data.get('last_login'),
                    user_data['id']
                )
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Database error updating user: {e}")
            return False
    
    def save_user_session(self, user_id, token, expires_at):
        """
        Save user session
        
        Args:
            user_id (str): User ID
            token (str): JWT token
            expires_at (str): Expiration timestamp
            
        Returns:
            str: Session ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate UUID for session
            session_id = str(uuid.uuid4())
            
            cursor.execute(
                """
                INSERT INTO user_sessions (
                    id, user_id, token, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    user_id,
                    token,
                    datetime.now().isoformat(),
                    expires_at
                )
            )
            
            conn.commit()
            conn.close()
            
            return session_id
            
        except sqlite3.Error as e:
            logger.error(f"Database error saving user session: {e}")
            raise
    
    def get_user_session(self, token):
        """
        Get user session by token
        
        Args:
            token (str): JWT token
            
        Returns:
            dict: Session record or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM user_sessions WHERE token = ?",
                (token,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Database error getting user session: {e}")
            return None
    
    def delete_user_session(self, token):
        """
        Delete user session
        
        Args:
            token (str): JWT token
            
        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM user_sessions WHERE token = ?",
                (token,)
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Database error deleting user session: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """
        Clean up expired sessions
        
        Returns:
            int: Number of deleted sessions
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM user_sessions WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
            
        except sqlite3.Error as e:
            logger.error(f"Database error cleaning up expired sessions: {e}")
            return 0

# Function to extend existing db_service with auth methods
def extend_db_service_with_auth(db_service, db_path):
    """
    Extend existing db_service with authentication methods
    
    Args:
        db_service: Existing database service
        db_path (str): Database path
        
    Returns:
        object: Extended database service
    """
    auth_db = AuthDBService(db_path)
    
    # Add auth methods to existing db_service
    db_service.get_user_by_google_id = auth_db.get_user_by_google_id
    db_service.get_user_by_email = auth_db.get_user_by_email
    db_service.get_user_by_id = auth_db.get_user_by_id
    db_service.create_user = auth_db.create_user
    db_service.update_user = auth_db.update_user
    db_service.save_user_session = auth_db.save_user_session
    db_service.get_user_session = auth_db.get_user_session
    db_service.delete_user_session = auth_db.delete_user_session
    db_service.cleanup_expired_sessions = auth_db.cleanup_expired_sessions
    
    return db_service