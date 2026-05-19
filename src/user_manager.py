"""
User management system for multi-user support in prostate MRI segmentation tool
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import hashlib
import secrets


class UserManager:
    """Manages user authentication and multi-user support"""

    def __init__(self, storage_path: str = "./user_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.users_file = self.storage_path / "users.json"
        self.sessions_file = self.storage_path / "sessions.json"
        self.load_users()
        self.load_sessions()

    def load_users(self):
        """Load existing user data"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except Exception:
                self.users = {}
        else:
            self.users = {}

    def load_sessions(self):
        """Load existing session data"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    self.sessions = json.load(f)
            except Exception:
                self.sessions = {}
        else:
            self.sessions = {}

    def save_users(self):
        """Save user data to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")

    def save_sessions(self):
        """Save session data to file"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")

    def create_user(self, username: str, email: str, password: str,
                   role: str = "user") -> bool:
        """
        Create a new user account

        Args:
            username: Unique username
            email: User's email address
            password: User's password
            role: User role (user, admin, researcher)

        Returns:
            Success status
        """
        if username in self.users:
            return False  # User already exists

        # Hash the password
        password_hash = self._hash_password(password)

        self.users[username] = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'is_active': True
        }

        self.save_users()
        return True

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user

        Args:
            username: Username
            password: Password

        Returns:
            User data if authentication successful, None otherwise
        """
        if username not in self.users:
            return None

        user = self.users[username]
        if not user['is_active']:
            return None

        if self._verify_password(password, user['password_hash']):
            # Update last login
            user['last_login'] = datetime.now().isoformat()
            self.save_users()
            return user

        return None

    def _hash_password(self, password: str) -> str:
        """Hash a password with salt"""
        salt = secrets.token_hex(16)
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
        return salt + pwdhash.hex()

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against stored hash"""
        salt = stored_hash[:32]
        stored_pwdhash = stored_hash[32:]
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
        return pwdhash.hex() == stored_pwdhash

    def create_session(self, username: str) -> Optional[str]:
        """
        Create a new session for a user

        Args:
            username: Username

        Returns:
            Session token if successful, None otherwise
        """
        if username not in self.users:
            return None

        # Generate a secure session token
        session_token = secrets.token_urlsafe(32)

        self.sessions[session_token] = {
            'username': username,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }

        self.save_sessions()
        return session_token

    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Validate a session token

        Args:
            session_token: Session token to validate

        Returns:
            Session data if valid, None otherwise
        """
        if session_token not in self.sessions:
            return None

        session = self.sessions[session_token]
        session['last_activity'] = datetime.now().isoformat()
        self.save_sessions()
        return session

    def end_session(self, session_token: str) -> bool:
        """
        End a user session

        Args:
            session_token: Session token to end

        Returns:
            Success status
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            self.save_sessions()
            return True
        return False

    def get_user_tasks(self, username: str) -> List[Dict]:
        """
        Get tasks assigned to a user

        Args:
            username: Username

        Returns:
            List of user's tasks
        """
        # This would be implemented based on how tasks are tracked
        # For now, returning empty list
        return []

    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get user information

        Args:
            username: Username

        Returns:
            User information or None
        """
        return self.users.get(username)

    def get_all_users(self) -> List[Dict]:
        """
        Get list of all users

        Returns:
            List of all users
        """
        return list(self.users.values())

    def update_user_role(self, username: str, new_role: str) -> bool:
        """
        Update a user's role

        Args:
            username: Username
            new_role: New role

        Returns:
            Success status
        """
        if username not in self.users:
            return False

        self.users[username]['role'] = new_role
        self.save_users()
        return True

    def deactivate_user(self, username: str) -> bool:
        """
        Deactivate a user account

        Args:
            username: Username

        Returns:
            Success status
        """
        if username not in self.users:
            return False

        self.users[username]['is_active'] = False
        self.save_users()
        return True


# Web-based user management for multi-user support
class WebUserManager(UserManager):
    """Enhanced user manager for web-based multi-user support"""

    def __init__(self, storage_path: str = "./user_data"):
        super().__init__(storage_path)
        self.active_users = {}  # Track currently active users in web context

    def register_web_user(self, username: str, session_token: str):
        """Register a user for web session tracking"""
        self.active_users[session_token] = {
            'username': username,
            'registered_at': datetime.now().isoformat()
        }

    def unregister_web_user(self, session_token: str):
        """Unregister a user from web session tracking"""
        if session_token in self.active_users:
            del self.active_users[session_token]

    def get_active_users(self) -> List[Dict]:
        """Get list of currently active web users"""
        return list(self.active_users.values())

    def get_user_activity(self, username: str) -> List[Dict]:
        """Get user activity history (would be implemented with status tracker)"""
        # Placeholder - in a real implementation, this would use the status tracker
        return []