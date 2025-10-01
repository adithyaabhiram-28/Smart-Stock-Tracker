import os
from dotenv import load_dotenv
from supabase import create_client, Client
 
load_dotenv()  # loads .env from project root
 
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
 
def get_supabase() -> Client:
    """
    Return a supabase client. Raises RuntimeError if config missing.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment (.env)")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# pip install -r requirements.txt
