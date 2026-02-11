
import os
import django
from dotenv import load_dotenv

# Load .env explicitly to ensure we read from file
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from django.conf import settings

print("Checking Django Cloudinary Configuration:")
try:
    cloud_config = settings.CLOUDINARY_STORAGE
    print(f"Cloud Name: {cloud_config.get('CLOUD_NAME')}")
    print(f"API Key: {cloud_config.get('API_KEY')}")
    secret = cloud_config.get('API_SECRET')
    print(f"API Secret (masked): {secret[:4]}...{secret[-4:]} (Length: {len(secret)})")
    
    # Try to verify configuration against cloudinary library
    import cloudinary
    print(f"Cloudinary Base Config: {cloudinary.config().cloud_name}")
except Exception as e:
    print(f"Error accessing settings: {e}")
