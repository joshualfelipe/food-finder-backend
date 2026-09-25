from config import settings
from supabase import Client, create_client

client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
db_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SECRET_KEY)
