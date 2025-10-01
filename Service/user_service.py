import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DAO.user_dao import UserDAO

class NoUser(Exception):
    pass

class UserService():
    def __init__(self):
        self.user_dao = UserDAO()
    def register_user(self, name : str, email : str):
        """Register a new user if email not taken"""
        if self.user_dao.get_user_by_email(email):
            raise ValueError("User already exists")
        return self.user_dao.create_user(name,email)
    def update_profile(self, user_id, name, email):
        """Update user profile"""
        return self.user_dao.update_user(user_id, name, email)

    def delete_account(self, user_id):
        """Delete user account"""
        return self.user_dao.delete_user(user_id)