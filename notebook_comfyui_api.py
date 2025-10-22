"""
ComfyUI API Server for Modal Notebooks with SocketIO Support
Paste this file into your Modal notebook and run it!

Usage in Modal Notebook:
    python notebook_comfyui_api.py
"""

# CRITICAL: Eventlet monkey patching MUST be first, before any other imports
import eventlet
eventlet.monkey_patch()

import os
import sys
import json
import uuid
import requests
import subprocess
import time
import threading
import base64
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit

# Force unbuffered output so logs show immediately in Modal
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

def log(message):
    """Print with immediate flush"""
    print(message, flush=True)

# Configuration
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1429488694498295899/soU4ivZA_7-bQ4TU2NMsp_8bLLPw0Gf1Qx9UB0Dh-wS5cLQ03n17ivQr0ijqRqheiehw"
COMFYUI_DIR = "/root/ComfyUI"
PORT = 8188
API_PORT = 5000

# Add ComfyUI to path
sys.path.insert(0, COMFYUI_DIR)

app = Flask(__name__)

# Initialize SocketIO with CORS support for ngrok URLs
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Track connected users {user_id: session_id}
connected_users = {}

# Aspect ratio presets (Fixed pixel budget ~2.4M pixels for consistent quality/speed)
ASPECT_RATIOS = {
    "1:1": (1536, 1536),    # Square - Instagram, general
    "16:9": (2048, 1152),   # Landscape - YouTube, monitors
    "9:16": (1152, 2048),   # Portrait - TikTok, mobile
    "4:3": (1776, 1328),    # Standard - Classic photos
    "3:2": (1888, 1256),    # Photo - DSLR standard
    "21:9": (2400, 1024),   # Cinematic - Ultra-wide
}

# High-Quality FLUX workflow
# Optimized for better detail, resolution, and rendering quality
DEFAULT_WORKFLOW = {
    "3": {
        "inputs": {
            "seed": 42,
            "steps": 30,  # Increased from 4 to 30 for much better quality
            "cfg": 3.5,   # Increased from 1 to 3.5 for better prompt adherence
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1,
            "model": ["10", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
    },
    "4": {
        "inputs": {
            "clip_name1": "clip_l.safetensors",
            "clip_name2": "t5xxl_fp16.safetensors",
            "type": "flux"
        },
        "class_type": "DualCLIPLoader"
    },
    "5": {
        "inputs": {
            "width": 1536,  # Increased from 1024 to 1536 for higher resolution
            "height": 1536, # Increased from 1024 to 1536 for higher resolution
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage"
    },
    "6": {
        "inputs": {
            "text": "a beautiful landscape, high quality, detailed, 8k, professional photography",
            "clip": ["4", 0]
        },
        "class_type": "CLIPTextEncode"
    },
    "7": {
        "inputs": {
            "text": "low quality, blurry, pixelated, low resolution, distorted, ugly, deformed",
            "clip": ["4", 0]
        },
        "class_type": "CLIPTextEncode"
    },
    "8": {
        "inputs": {
            "samples": ["3", 0],
            "vae": ["11", 0]
        },
        "class_type": "VAEDecode"
    },
    "10": {
        "inputs": {
            "unet_name": "flux1-krea-dev.safetensors",
            "weight_dtype": "default"
        },
        "class_type": "UNETLoader"
    },
    "11": {
        "inputs": {
            "vae_name": "ae.safetensors"
        },
        "class_type": "VAELoader"
    },
    "9": {
        "inputs": {
            "filename_prefix": "ComfyUI_HQ",
            "images": ["8", 0]
        },
        "class_type": "SaveImage"
    }
}

def start_comfyui():
    """Start ComfyUI in the background"""
    log("🚀 Starting ComfyUI...")
    
    # Start ComfyUI
    cmd = f"cd {COMFYUI_DIR} && python main.py --listen 0.0.0.0 --port {PORT}"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for ComfyUI to start
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(f"http://localhost:{PORT}/system_stats")
            if response.status_code == 200:
                log("✅ ComfyUI is ready!")
                return True
        except:
            pass
        time.sleep(2)
        log(f"⏳ Waiting for ComfyUI... ({i+1}/{max_attempts})")
    
    log("❌ ComfyUI failed to start")
    return False

def send_discord_notification(url):
    """Send Discord notification with API URL"""
    log("📬 Sending Discord notification...")
    if not DISCORD_WEBHOOK:
        log("   ⚠️  No Discord webhook configured")
        return
    
    message = {
        "embeds": [{
            "title": "🎨 ComfyUI API is Live!",
            "description": f"Your ComfyUI API is running in Modal Notebook",
            "color": 5814783,
            "fields": [
                {
                    "name": "📡 Generate Endpoint",
                    "value": f"`POST {url}/generate`",
                    "inline": False
                },
                {
                    "name": "💚 Health Check",
                    "value": f"`GET {url}/health`",
                    "inline": False
                },
                {
                    "name": "🎯 Example Usage",
                    "value": f"```bash\ncurl -X POST {url}/generate \\\n  -H 'Content-Type: application/json' \\\n  -d '{{\"prompt\": \"a beautiful sunset\"}}' \\\n  --output image.png\n```",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Made with ❤️ for AI Art"
            }
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=message)
        if response.status_code == 204:
            log("   ✅ Discord notification sent successfully!")
        else:
            log(f"   ⚠️  Discord returned status: {response.status_code}")
    except Exception as e:
        log(f"   ❌ Failed to send Discord notification: {e}")

def queue_prompt(workflow):
    """Queue a prompt to ComfyUI"""
    try:
        p = {"prompt": workflow, "client_id": str(uuid.uuid4())}
        response = requests.post(f"http://localhost:{PORT}/prompt", json=p)
        return response.json()
    except Exception as e:
        print(f"Error queuing prompt: {e}")
        return None

def get_image(filename, subfolder, folder_type):
    """Get generated image from ComfyUI"""
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    response = requests.get(f"http://localhost:{PORT}/view", params=params)
    return response.content

def wait_for_completion(prompt_id):
    """Wait for image generation to complete"""
    max_wait = 900  # Increased to 15 minutes for high-quality generation
    start_time = time.time()
    last_progress_log = 0
    
    log(f"⏳ Waiting for high-quality generation (max {max_wait}s)...")
    
    while time.time() - start_time < max_wait:
        elapsed = time.time() - start_time
        
        # Log progress every 30 seconds
        if elapsed - last_progress_log >= 30:
            log(f"⏱️  Generation in progress... {int(elapsed)}s elapsed (quality mode: 30 steps @ 1536×1536)")
            last_progress_log = elapsed
        
        try:
            response = requests.get(f"http://localhost:{PORT}/history/{prompt_id}")
            history = response.json()
            
            if prompt_id in history:
                prompt_data = history[prompt_id]
                
                # Check for errors in execution
                status = prompt_data.get("status", {})
                if "status_str" in status and status["status_str"] == "error":
                    log(f"❌ ComfyUI execution error detected!")
                    log(f"   Error details: {json.dumps(status, indent=2)}")
                    return {"error": status, "prompt_id": prompt_id}
                
                # Check if there are error messages
                if "messages" in status and status["messages"]:
                    log(f"⚠️  ComfyUI messages: {status['messages']}")
                
                # Check for outputs
                outputs = prompt_data.get("outputs", {})
                if outputs:
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            log(f"✅ High-quality image generation complete after {int(elapsed)}s!")
                            return node_output["images"][0]
        except Exception as e:
            log(f"⚠️  Error checking history: {e}")
        
        time.sleep(1)
    
    # Timeout - try to get the last known status
    try:
        response = requests.get(f"http://localhost:{PORT}/history/{prompt_id}")
        history = response.json()
        if prompt_id in history:
            log(f"⚠️  Timeout! Last known status:")
            log(f"   {json.dumps(history[prompt_id].get('status', {}), indent=2)}")
    except:
        pass
    
    return None

# ============================================
# SocketIO Event Handlers
# ============================================

# Catch-all event handler for debugging
@socketio.on_error_default
def default_error_handler(e):
    log(f"❌ SocketIO Error: {e}")
    import traceback
    log(traceback.format_exc())

# Catch ANY event that isn't explicitly handled
@socketio.on('*')
def catch_all(event, data):
    log(f"🔔 CATCH-ALL: Received event '{event}' with data: {data}")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        user_id = str(uuid.uuid4())
        connected_users[user_id] = request.sid
        emit('connected', {'user_id': user_id, 'message': 'Connected to ComfyUI API'})
        log(f"✅ WebSocket connected: User {user_id[:8]}... (sid: {request.sid})")
        log(f"📊 Total connected users: {len(connected_users)}")
    except Exception as e:
        log(f"❌ Error in connect handler: {e}")
        import traceback
        log(traceback.format_exc())

@socketio.on('disconnect')
def handle_disconnect(reason=None):
    """Handle client disconnection"""
    try:
        # Find and remove user
        disconnect_reason = f" (reason: {reason})" if reason else ""
        for uid, sid in list(connected_users.items()):
            if sid == request.sid:
                del connected_users[uid]
                log(f"❌ WebSocket disconnected: User {uid[:8]}...{disconnect_reason}")
                log(f"📊 Remaining connected users: {len(connected_users)}")
                break
    except Exception as e:
        log(f"❌ Error in disconnect handler: {e}")
        import traceback
        log(traceback.format_exc())

def _handle_generation_request(data, event_name):
    """Common handler for generation requests (used by both 'generate' and 'generate_image')"""
    try:
        log(f"🔔 RAW EVENT RECEIVED: {event_name}")
        log(f"📦 Raw data received: {data}")
        log(f"📦 Data type: {type(data)}")
        
        # Validate data
        if not data:
            log(f"⚠️ No data received in {event_name} event")
            emit('generation_error', {
                'status': 'error',
                'error': 'No data provided',
                'message': 'Please provide prompt and user_id'
            })
            return
        
        user_id = data.get('user_id') if isinstance(data, dict) else None
        prompt = data.get('prompt', 'a beautiful landscape') if isinstance(data, dict) else 'a beautiful landscape'
        aspect_ratio = data.get('aspect_ratio', '1:1') if isinstance(data, dict) else '1:1'  # NEW!
        
        if not user_id:
            log(f"⚠️ No user_id in data. Data keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
            emit('generation_error', {
                'status': 'error',
                'error': 'Missing user_id',
                'message': 'user_id is required'
            })
            return
        
        # Get dimensions from aspect ratio
        if aspect_ratio not in ASPECT_RATIOS:
            log(f"⚠️ Invalid aspect ratio '{aspect_ratio}', defaulting to 1:1")
            aspect_ratio = '1:1'
        
        width, height = ASPECT_RATIOS[aspect_ratio]
        
        log(f"🎨 SocketIO generation request from user {user_id[:8]}...: '{prompt}'")
        log(f"📐 Aspect ratio: {aspect_ratio} → {width}×{height} ({width*height:,} pixels)")
        log(f"👤 User session ID: {connected_users.get(user_id, 'NOT FOUND')}")
        
        # Run generation in background thread to keep socket alive
        log(f"🚀 Starting background generation thread...")
        threading.Thread(target=generate_and_emit, args=(user_id, prompt, width, height, aspect_ratio), daemon=True).start()
        
        # Send immediate acknowledgment
        emit('generation_started', {
            'status': 'started',
            'message': f'Generating high-quality image for: "{prompt}"',
            'estimated_time': f'120-180 seconds (high quality mode: 30 steps @ {width}×{height})',
            'prompt': prompt,
            'quality_mode': 'high',
            'resolution': f'{width}×{height}',
            'aspect_ratio': aspect_ratio,
            'steps': 30,
            'total_pixels': width * height
        })
        log(f"✅ Sent generation_started acknowledgment to user {user_id[:8]}...")
        log(f"✅ Generation task queued for background processing")
        
    except Exception as e:
        log(f"❌ Error in {event_name} handler: {e}")
        import traceback
        log(traceback.format_exc())
        emit('generation_error', {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to process generation request'
        })

@socketio.on('generate_image')
def handle_generate_image(data):
    """Handle real-time image generation request via WebSocket (event: generate_image)"""
    _handle_generation_request(data, 'generate_image')

@socketio.on('generate')
def handle_generate(data):
    """Handle real-time image generation request via WebSocket (event: generate)"""
    _handle_generation_request(data, 'generate')

def generate_and_emit(user_id, prompt, width=1536, height=1536, aspect_ratio="1:1"):
    """Generate image and emit to specific user"""
    try:
        log(f"⌛ Starting generation for user {user_id[:8]}...")
        log(f"📐 Resolution: {width}×{height} (aspect ratio: {aspect_ratio})")
        
        # Enhance prompt with quality keywords
        enhanced_prompt = f"{prompt}, high quality, detailed, sharp focus, professional, 8k uhd, masterpiece"
        log(f"✨ Enhanced prompt: '{enhanced_prompt}'")
        
        # Update workflow with enhanced prompt and dynamic dimensions
        workflow = DEFAULT_WORKFLOW.copy()
        
        # Set dynamic dimensions
        if "5" in workflow:
            workflow["5"]["inputs"]["width"] = width
            workflow["5"]["inputs"]["height"] = height
            log(f"✅ Workflow updated with {width}×{height} dimensions")
        
        # Set enhanced prompt
        if "6" in workflow:
            workflow["6"]["inputs"]["text"] = enhanced_prompt
        
        # Queue the prompt
        result = queue_prompt(workflow)
        if not result or "prompt_id" not in result:
            raise Exception("Failed to queue prompt")
        
        prompt_id = result["prompt_id"]
        log(f"✅ Queued prompt {prompt_id} for user {user_id[:8]}...")
        
        # Send progress update
        sid = connected_users.get(user_id)
        if sid:
            socketio.emit('generation_progress', {
                'status': 'processing',
                'message': 'Image is being generated...',
                'prompt_id': prompt_id
            }, to=sid)
        
        # Wait for completion
        start_time = time.time()
        image_info = wait_for_completion(prompt_id)
        elapsed = time.time() - start_time
        
        if not image_info:
            raise Exception("Generation timeout or failed")
        
        # Check if ComfyUI returned an error
        if "error" in image_info:
            error_details = image_info.get("error", {})
            error_msg = "ComfyUI execution failed"
            
            # Try to extract useful error message
            if "messages" in error_details:
                for msg in error_details.get("messages", []):
                    if isinstance(msg, list) and len(msg) > 1:
                        if msg[0] == "execution_error":
                            error_data = msg[1]
                            exception_msg = error_data.get("exception_message", "Unknown error")
                            node_type = error_data.get("node_type", "Unknown")
                            error_msg = f"ComfyUI error in {node_type}: {exception_msg}"
                            break
            
            log(f"❌ ComfyUI execution error: {error_msg}")
            raise Exception(error_msg)
        
        # Check if we have a filename (successful generation)
        if "filename" not in image_info:
            log(f"❌ No filename in image_info. Got: {image_info}")
            raise Exception("Image generation failed - no filename returned")
        
        # Get the image
        image_data = get_image(
            image_info["filename"],
            image_info.get("subfolder", ""),
            image_info.get("type", "output")
        )
        
        log(f"✅ Image generated in {elapsed:.1f}s for user {user_id[:8]}...")
        
        # Option 1: Send as base64 (works without external hosting)
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Send to specific user
        if sid:
            socketio.emit('image_ready', {
                'status': 'complete',
                'image_data': f'data:image/png;base64,{image_base64}',
                'prompt': prompt,
                'generation_time': elapsed,
                'size_bytes': len(image_data)
            }, to=sid)
            log(f"📤 Sent image to user {user_id[:8]}... via SocketIO")
        else:
            log(f"⚠️ User {user_id[:8]}... disconnected before image was ready")
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        log(f"❌ Error generating for user {user_id[:8]}...: {e}")
        log(error_trace)
        
        # Send error to user
        sid = connected_users.get(user_id)
        if sid:
            socketio.emit('generation_error', {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to generate image'
            }, to=sid)

# ============================================
# REST API Routes
# ============================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        response = requests.get(f"http://localhost:{PORT}/system_stats")
        if response.status_code == 200:
            return jsonify({"status": "healthy", "comfyui": "running"})
    except:
        pass
    
    return jsonify({"status": "unhealthy", "comfyui": "not running"}), 503

@app.route('/generate', methods=['POST'])
def generate():
    """Generate image from prompt"""
    log("\n" + "="*60)
    log("🎨 NEW IMAGE GENERATION REQUEST")
    log("="*60)
    
    try:
        # Parse request
        log("📥 Parsing request data...")
        data = request.json
        log(f"   Request data: {data}")
        
        prompt = data.get("prompt", "a beautiful landscape")
        workflow = data.get("workflow", DEFAULT_WORKFLOW.copy())
        
        log(f"📝 Prompt: '{prompt}'")
        
        # Update prompt in workflow
        if "6" in workflow:
            workflow["6"]["inputs"]["text"] = prompt
            log("✅ Prompt injected into workflow")
        
        # Queue the prompt
        log("📤 Queuing prompt to ComfyUI...")
        log(f"   ComfyUI URL: http://localhost:{PORT}/prompt")
        
        try:
            result = queue_prompt(workflow)
            log(f"📥 Queue result: {result}")
        except Exception as e:
            log(f"❌ Failed to queue prompt: {e}")
            return jsonify({"error": f"Failed to queue: {str(e)}"}), 500
        
        if not result or "prompt_id" not in result:
            log(f"❌ Invalid queue result: {result}")
            return jsonify({"error": "Failed to queue prompt", "details": str(result)}), 500
        
        prompt_id = result["prompt_id"]
        log(f"✅ Prompt queued successfully!")
        log(f"   Prompt ID: {prompt_id}")
        
        # Wait for completion
        log("⏳ Waiting for generation to complete...")
        log("   (This may take 1-5 minutes for FLUX models)")
        
        start_time = time.time()
        image_info = wait_for_completion(prompt_id)
        elapsed = time.time() - start_time
        
        log(f"⏱️  Generation took {elapsed:.1f} seconds")
        log(f"📊 Image info: {image_info}")
        
        if not image_info:
            log("❌ Generation timeout or failed!")
            return jsonify({"error": "Generation timeout"}), 500
        
        # Get the image
        log(f"📥 Downloading generated image...")
        log(f"   Filename: {image_info.get('filename', 'unknown')}")
        log(f"   Subfolder: {image_info.get('subfolder', 'none')}")
        log(f"   Type: {image_info.get('type', 'output')}")
        
        try:
            image_data = get_image(
                image_info["filename"],
                image_info.get("subfolder", ""),
                image_info.get("type", "output")
            )
            log(f"✅ Image downloaded successfully!")
            log(f"   Size: {len(image_data):,} bytes ({len(image_data)/1024/1024:.2f} MB)")
        except Exception as e:
            log(f"❌ Failed to download image: {e}")
            return jsonify({"error": f"Failed to get image: {str(e)}"}), 500
        
        # Save temporarily and send
        temp_path = f"/tmp/{uuid.uuid4()}.png"
        with open(temp_path, "wb") as f:
            f.write(image_data)
        
        log(f"💾 Image saved to: {temp_path}")
        log("📤 Sending image to client...")
        log("✅ IMAGE GENERATION COMPLETE!")
        log("="*60 + "\n")
        
        return send_file(temp_path, mimetype="image/png")
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        log("\n" + "="*60)
        log("❌ ERROR IN /generate ROUTE")
        log("="*60)
        log(f"Error: {str(e)}")
        log("\nFull traceback:")
        log(error_trace)
        log("="*60 + "\n")
        return jsonify({"error": str(e), "traceback": error_trace}), 500

@app.route('/list-models', methods=['GET'])
def list_models():
    """List available models"""
    models_dir = Path(COMFYUI_DIR) / "models" / "checkpoints"
    models = []
    
    if models_dir.exists():
        models = [f.name for f in models_dir.iterdir() if f.suffix in ['.safetensors', '.ckpt', '.pt']]
    
    return jsonify({"models": models})

def get_notebook_url():
    """Get the public URL of the Modal notebook"""
    # In Modal notebooks, you'll need to use ngrok or similar
    # For now, return localhost
    return f"http://localhost:{API_PORT}"

def main():
    """Main function to start the server"""
    log("=" * 60)
    log("🎨 ComfyUI API Server for Modal Notebooks with SocketIO")
    log("=" * 60)
    
    # Log registered SocketIO event handlers
    log("\n🔌 SocketIO Event Handlers Registered:")
    for event in socketio.handlers:
        if event in socketio.handlers and socketio.handlers[event]:
            log(f"   ✅ '{event}' handler registered")
    log("")
    
    # Start ComfyUI
    if not start_comfyui():
        log("❌ Failed to start ComfyUI. Exiting...")
        return
    
    # Get public URL (you may need to set this manually in Modal)
    url = get_notebook_url()
    
    # Send Discord notification
    send_discord_notification(url)
    
    log("\n" + "=" * 60)
    log("✅ API Server Started!")
    log("=" * 60)
    log(f"\n📡 Endpoints:")
    log(f"   POST {url}/generate      - Generate images")
    log(f"   GET  {url}/health        - Health check")
    log(f"   GET  {url}/list-models   - List models")
    log("\n🎯 Example:")
    log(f"   curl -X POST {url}/generate \\")
    log(f"     -H 'Content-Type: application/json' \\")
    log(f"     -d '{{\"prompt\": \"a beautiful sunset\"}}' \\")
    log(f"     --output image.png")
    log("\n" + "=" * 60)
    log("\n🔍 Watching for requests... (logs will appear below)")
    log("="*60 + "\n")
    
    # Start Flask app with SocketIO support
    socketio.run(app, host='0.0.0.0', port=API_PORT, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()

