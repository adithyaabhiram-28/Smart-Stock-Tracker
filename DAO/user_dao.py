import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_supabase

class UserDAO:
    def __init__(self):
        self.sb = get_supabase()
    def create_user(self, name : str, email : str):
        """ Add new user to database """
        if self.get_user_by_email(email):
            raise ValueError("User already exists")
        resp = self.sb.table("users").insert({"name": name, "email": email}).execute()
        return resp
    def get_user_by_id(self,user_id):
        resp = self.sb.table("users").select("*").eq("user_id", user_id).execute()
        return resp.data[0] if resp.data else None
    def get_user_by_email(self,email):
        resp = self.sb.table("users").select("*").eq("email", email).execute()
        return resp.data[0] if resp.data else None
    def update_user(self,user_id,name,email):
        """Update user details"""
        resp = self.sb.table("users").update({"name" : name , "email" : email}).eq("user_id", user_id).execute()
        return resp.data
    def delete_user(self,user_id):
        """Delete user only if it exists"""
        if not self.get_user_by_id(user_id):
            raise ValueError("User not found")
        resp = self.sb.table("users").delete().eq("user_id", user_id).execute()
        return resp
    