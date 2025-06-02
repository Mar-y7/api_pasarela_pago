from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Leer las variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Validar
if not SUPABASE_URL or not SUPABASE_API_KEY:
    raise RuntimeError("❌ Faltan las variables SUPABASE_URL o SUPABASE_API_KEY en el archivo .env")

# Crear el cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)
