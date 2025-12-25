import os
import sys
import certifi

# Fix SSL certificate verification error on macOS
os.environ['SSL_CERT_FILE'] = certifi.where()

import uvicorn
from pyngrok import ngrok
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_ngrok():
    # Kill any existing ngrok tunnels to avoid conflicts
    # ngrok.kill() # Optional: might be too aggressive if user has other tunnels

    # Get port from env or default to 8000
    port = int(os.getenv("PORT", 8000))

    # Open a HTTP tunnel on the default port 8000
    # verify_ssl=False might be needed if local self-signed certs are issues, 
    # but for http localhost it's usually fine.
    public_url = ngrok.connect(port).public_url
    
    print("=" * 50)
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")
    print(f" * Webhook URL: {public_url}/callback")
    print("=" * 50)
    
    # Update the URL in simple text file or just print it? 
    # Just printing is good for now.

    return port

if __name__ == "__main__":
    try:
        port = start_ngrok()
        # Start the uvicorn server
        # We use the same app:app module string
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
    except KeyboardInterrupt:
        print("\nStopping...")
        ngrok.kill()
        sys.exit(0)
