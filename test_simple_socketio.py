#!/usr/bin/env python3
"""
Simple SocketIO test client to verify events are being received
Run this from your local machine to test the Modal server
"""

import socketio
import time
import sys

# Replace with your ngrok URL
SERVER_URL = input("Enter your ngrok URL (e.g., https://abc123.ngrok-free.app): ").strip()

if not SERVER_URL:
    print("❌ No URL provided!")
    sys.exit(1)

print(f"\n🔄 Connecting to {SERVER_URL}...")

# Create SocketIO client
sio = socketio.Client()

user_id = None

@sio.event
def connect():
    print("✅ Connected to server!")

@sio.event
def connected(data):
    global user_id
    user_id = data['user_id']
    print(f"✅ Received user_id: {user_id}")
    print(f"📝 Message: {data.get('message', 'N/A')}")

@sio.event
def disconnect():
    print("❌ Disconnected from server")

@sio.event
def generation_started(data):
    print(f"🎨 Generation started: {data.get('message', 'N/A')}")
    print(f"⏱️  Estimated time: {data.get('estimated_time', 'N/A')}")

@sio.event
def generation_progress(data):
    print(f"⏳ Progress: {data.get('message', 'N/A')}")

@sio.event
def image_ready(data):
    print(f"✅ Image ready!")
    print(f"⏱️  Generation time: {data.get('generation_time', 0):.1f}s")
    print(f"📦 Size: {data.get('size_bytes', 0) / 1024 / 1024:.2f} MB")
    print(f"📝 Prompt: {data.get('prompt', 'N/A')}")
    print("\n✨ Image received! Check your browser if using HTML client.")

@sio.event
def generation_error(data):
    print(f"❌ Generation error: {data.get('message', 'N/A')}")
    print(f"❌ Error details: {data.get('error', 'N/A')}")

try:
    # Connect to server
    sio.connect(SERVER_URL)
    
    # Wait for user_id
    print("⏳ Waiting for user_id...")
    time.sleep(2)
    
    if not user_id:
        print("❌ Did not receive user_id! Check server logs.")
        sio.disconnect()
        sys.exit(1)
    
    # Get prompt from user
    print("\n" + "="*60)
    prompt = input("Enter prompt (or press Enter for default): ").strip()
    if not prompt:
        prompt = "a beautiful sunset over mountains"
    
    print(f"\n📤 Sending generation request...")
    print(f"   User ID: {user_id}")
    print(f"   Prompt: {prompt}")
    
    # Send generate_image event
    sio.emit('generate_image', {
        'user_id': user_id,
        'prompt': prompt
    })
    
    print("✅ Request sent! Waiting for response...")
    print("   (Check your Modal notebook logs for server-side logging)")
    print("\n" + "="*60)
    
    # Wait for response (up to 5 minutes)
    print("\n⏳ Waiting for image generation...")
    time.sleep(300)
    
except KeyboardInterrupt:
    print("\n\n👋 Interrupted by user")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if sio.connected:
        sio.disconnect()
    print("\n✅ Test complete!")
