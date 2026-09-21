from config import settings
from supabase import Client, create_client

client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
