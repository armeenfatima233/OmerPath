# SERVER-SIDE ONLY. Uses a privileged Supabase secret key — must never be
# imported into frontend/React code or otherwise exposed to the client.
import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_SECRET_KEY must be set in the environment"
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)
