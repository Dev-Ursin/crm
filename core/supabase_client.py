import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("Defina SUPABASE_URL e SUPABASE_ANON_KEY no .env")
    return create_client(url, key)

