import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Service.user_service import UserService
from Client.portfolio_cli import PortfolioCLI

class UserCLI:
    def __init__(self):
        self.user_service = UserService()
        self.current_user  = None
    def menu(self):
        while True:
            print("\n--- Smart Stock Tracker ---")
            print("1. Register")
            print("2. Login")
            print("3. Update Profile")
            print("4. Delete Account")
            print("5. Exit")
            choice = input("Enter choice: ")
            if choice == "1":
                self.register()
            elif choice == "2":
                self.login()
            elif choice == "3":
                self.update_profile()
            elif choice == "4":
                self.delete_account()
            elif choice == "5":
                print("Exiting...")
                break
            else:
                print("Invalid choice!")
    def register(self):
        name = input("Enter name: ")
        email = input("Enter email: ")
        try:
            user = self.user_service.register_user(name, email)
            print("User registered successfully:", user)
        except ValueError as e:
            print("Error:", e)

    def login(self):
        email = input("Enter email: ")
        user = self.user_service.user_dao.get_user_by_email(email)
        if user:
            self.current_user = user
            print("Logged in successfully as", user["name"])
            PortfolioCLI(user).menu()
        else:
            print("User not found!")

    def update_profile(self):
        if not self.current_user:
            print("Login first!")
            return
        name = input("Enter new name: ")
        email = input("Enter new email: ")
        try:
            updated_user = self.user_service.update_profile(self.current_user["user_id"], name, email)
            print("Profile updated:", updated_user)
        except ValueError as e:
            print("Error:", e)

    def delete_account(self):
        if not self.current_user:
            print("Login first!")
            return
        confirm = input("Are you sure? (y/n): ")
        if confirm.lower() == "y":
            self.user_service.delete_account(self.current_user["user_id"])
            print("Account deleted successfully!")
            self.current_user = None

if __name__ == "__main__":
    UserCLI().menu()