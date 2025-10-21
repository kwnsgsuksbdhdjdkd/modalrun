"""
Start ComfyUI API with ngrok for public access
Supports both REST API and WebSocket (SocketIO) connections
Run this in your Modal notebook for a public URL
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path

try:
    from pyngrok import ngrok
except ImportError:
    print("📦 Installing pyngrok...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok", "-q"])
    from pyngrok import ngrok

# Configuration
API_PORT = 5000
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1429488694498295899/soU4ivZA_7-bQ4TU2NMsp_8bLLPw0Gf1Qx9UB0Dh-wS5cLQ03n17ivQr0ijqRqheiehw"
NGROK_AUTH_TOKEN = "34I1jdUho1Jn8wo1QaRkocbxPkP_5bUtZxmGAGkVdtvctTDrb"  # Your ngrok token

def send_discord_notification(public_url):
    """Send Discord notification with public URL"""
    if not DISCORD_WEBHOOK:
        return
    
    message = {
        "embeds": [{
            "title": "🌍 ComfyUI API is Live with Public URL!",
            "description": "Your ComfyUI API is running in Modal Notebook with public access via ngrok",
            "color": 3066993,
            "fields": [
                {
                    "name": "🌐 Public URL",
                    "value": f"`{public_url}`",
                    "inline": False
                },
                {
                    "name": "📡 Generate Endpoint",
                    "value": f"`POST {public_url}/generate`",
                    "inline": False
                },
                {
                    "name": "💚 Health Check",
                    "value": f"`GET {public_url}/health`",
                    "inline": False
                },
                {
                    "name": "🎯 Example Usage",
                    "value": f"```bash\ncurl -X POST {public_url}/generate \\\n  -H 'Content-Type: application/json' \\\n  -d '{{\"prompt\": \"a beautiful sunset\"}}' \\\n  --output image.png\n```",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Made with ❤️ for AI Art | Powered by Modal + ngrok"
            }
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=message, timeout=10)
        if response.status_code == 204:
            print(f"✅ Discord notification sent!")
        else:
            print(f"⚠️  Discord notification failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Failed to send Discord notification: {e}")

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  🌍 ComfyUI API with Public URL (ngrok)               ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    # Configure ngrok auth token
    if NGROK_AUTH_TOKEN:
        print("🔑 Configuring ngrok authentication...")
        try:
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)
            print("✅ ngrok authenticated!")
        except Exception as e:
            print(f"⚠️  Warning: Could not set ngrok token: {e}")
    
    # Start ngrok tunnel
    print(f"🔗 Creating ngrok tunnel on port {API_PORT}...")
    try:
        # Kill any existing ngrok processes
        subprocess.run(["pkill", "-9", "ngrok"], stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        # Start new tunnel
        tunnel = ngrok.connect(API_PORT, bind_tls=True)
        public_url = tunnel.public_url  # Extract clean URL string
        print(f"✅ ngrok tunnel created!")
        print()
    except Exception as e:
        print(f"❌ Failed to create ngrok tunnel: {e}")
        print()
        print("💡 Tip: Make sure no other ngrok tunnels are running")
        return
    
    # Display URLs
    print("=" * 60)
    print(f"🌍 PUBLIC URL: {public_url}")
    print("=" * 60)
    print()
    print("📡 API Endpoints:")
    print(f"   POST {public_url}/generate")
    print(f"   GET  {public_url}/health")
    print(f"   GET  {public_url}/list-models")
    print()
    print("🎯 Example Usage:")
    print(f"   curl -X POST {public_url}/generate \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"prompt\": \"a beautiful sunset\"}}' \\")
    print(f"     --output image.png")
    print()
    print("=" * 60)
    print()
    
    # Send Discord notification
    send_discord_notification(public_url)
    
    # Start the API server
    print("🚀 Starting ComfyUI API server...")
    print("   (This will take a moment...)")
    print()
    
    try:
        # Start the API server as a subprocess
        api_process = subprocess.Popen(
            [sys.executable, "notebook_comfyui_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait a moment for Flask to start binding to port
        print("⏳ Waiting for Flask to start...")
        time.sleep(3)
        
        print("✅ API Server started!")
        print()
        print("=" * 60)
        print("🎉 Everything is running!")
        print("=" * 60)
        print()
        print(f"🌐 Your public API URL: {public_url}")
        print()
        print("📝 Press Ctrl+C to stop the server")
        print("💡 Keep this window open to keep the API running")
        print()
        
        # Keep the script running and show output
        try:
            while True:
                # Check if process is still running
                if api_process.poll() is not None:
                    print("❌ API server process stopped unexpectedly!")
                    stdout, stderr = api_process.communicate()
                    if stdout:
                        print("Output:", stdout[-500:])
                    break
                
                # Read and display output
                output = api_process.stdout.readline()
                if output:
                    print(output.strip())
                time.sleep(0.1)
        except KeyboardInterrupt:
            print()
            print("👋 Shutting down...")
            api_process.terminate()
            time.sleep(1)
            api_process.kill()
            ngrok.disconnect(tunnel.public_url)
            print("✅ Server stopped")
            
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        print()
        print("💡 Make sure notebook_comfyui_api.py exists in the current directory")

if __name__ == "__main__":
    # Check if notebook_comfyui_api.py exists
    if not Path("notebook_comfyui_api.py").exists():
        print("❌ Error: notebook_comfyui_api.py not found!")
        print()
        print("📁 Current directory:", os.getcwd())
        print()
        print("💡 Make sure you're in the correct directory with the API file.")
        sys.exit(1)
    
    main()

