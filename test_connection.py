import sys
import os
# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_supabase

supabase = get_supabase()
response = supabase.table("users").select("*").execute()
print("✅ Database connection successful!")
print(f"📊 Found {len(response.data)} users in database")
print(response.data)