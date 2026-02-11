
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load .env explicitly
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

print(f"Testing Cloudinary Connection...")
print(f"Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
print(f"API Key: {os.getenv('CLOUDINARY_API_KEY')}")
# Do not print the full secret for security, just length and first/last 4 chars if possible
# But also print repr to check for invisible chars
secret = os.getenv('CLOUDINARY_API_SECRET')
print(f"API Secret (repr): {repr(secret)}")
print(f"API Secret Length: {len(secret) if secret else 0}")

try:
    # Try to upload a test string as a file
    response = cloudinary.uploader.upload("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgADNjd8qAAAAABJRU5ErkJggg==", public_id="test_image")
    print("\nSUCCESS! Connection verified.")
    print(f"Image URL: {response.get('url')}")
except Exception as e:
    print("\nFAILED. Error details:")
    print(e)
