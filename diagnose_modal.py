#!/usr/bin/env python3
"""
Diagnostic script for Modal Notebook environment
Run this to check if everything is configured correctly
"""

import os
import sys
import subprocess

print("╔════════════════════════════════════════════════════════╗")
print("║         ComfyUI Modal Notebook Diagnostics             ║")
print("╚════════════════════════════════════════════════════════╝")
print()

# 1. Check Python version
print("📍 1. Python Version")
print(f"   Version: {sys.version}")
print(f"   Path: {sys.executable}")
print()

# 2. Check current directory
print("📍 2. Current Directory")
current_dir = os.getcwd()
print(f"   {current_dir}")
print()

# 3. Check project files
print("📍 3. Project Files in Current Directory")
files_to_check = [
    "notebook_comfyui_api.py",
    "start_with_ngrok.py",
    "notebook_setup.sh",
    "config.json"
]

for file in files_to_check:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"   ✅ {file} ({size} bytes)")
    else:
        print(f"   ❌ {file} - NOT FOUND!")
print()

# 4. Check ComfyUI installation
print("📍 4. ComfyUI Installation")
comfyui_dir = "/root/ComfyUI"
if os.path.exists(comfyui_dir):
    print(f"   ✅ ComfyUI directory exists: {comfyui_dir}")
    
    # Check main.py
    main_py = os.path.join(comfyui_dir, "main.py")
    if os.path.exists(main_py):
        print(f"   ✅ main.py found")
    else:
        print(f"   ❌ main.py NOT FOUND!")
else:
    print(f"   ❌ ComfyUI directory NOT FOUND: {comfyui_dir}")
    print(f"   💡 Install with: git clone https://github.com/comfyanonymous/ComfyUI.git /root/ComfyUI")
print()

# 5. Check models
print("📍 5. AI Models")
models_dir = "/root/ComfyUI/models/checkpoints"
if os.path.exists(models_dir):
    models = [f for f in os.listdir(models_dir) if f.endswith(('.safetensors', '.ckpt', '.pt'))]
    if models:
        print(f"   ✅ Found {len(models)} model(s):")
        for model in models:
            size = os.path.getsize(os.path.join(models_dir, model))
            size_gb = size / (1024**3)
            print(f"      - {model} ({size_gb:.2f} GB)")
    else:
        print(f"   ❌ No models found in {models_dir}")
        print(f"   💡 Download with:")
        print(f"      cd /root/ComfyUI/models/checkpoints")
        print(f"      wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors")
else:
    print(f"   ❌ Models directory NOT FOUND: {models_dir}")
print()

# 6. Check Python dependencies
print("📍 6. Python Dependencies")
required_packages = ['flask', 'requests', 'pyngrok', 'torch']
for package in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - NOT INSTALLED")
        print(f"      Install with: pip install {package}")
print()

# 7. Check ports
print("📍 7. Port Availability")
def check_port(port):
    try:
        result = subprocess.run(
            ['lsof', '-i', f':{port}'],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"   ⚠️  Port {port} is IN USE")
            print(f"      Process: {result.stdout.split()[0] if result.stdout.split() else 'Unknown'}")
            return False
        else:
            print(f"   ✅ Port {port} is available")
            return True
    except:
        print(f"   ⚠️  Cannot check port {port} (lsof not available)")
        return True

check_port(8188)  # ComfyUI port
check_port(5000)  # API port
print()

# 8. Test ComfyUI startup
print("📍 8. Testing ComfyUI Startup")
print("   Attempting to start ComfyUI...")
print("   (This will timeout after 5 seconds)")
try:
    process = subprocess.Popen(
        ['python', f'{comfyui_dir}/main.py', '--listen', '0.0.0.0', '--port', '8188'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait 5 seconds
    import time
    time.sleep(5)
    
    # Check if it's running
    if process.poll() is None:
        print("   ✅ ComfyUI started successfully!")
        process.terminate()
        time.sleep(1)
        process.kill()
    else:
        stdout, stderr = process.communicate()
        print("   ❌ ComfyUI failed to start")
        print("   Error output:")
        if stderr:
            print(f"      {stderr[:500]}")
        if stdout:
            print(f"      {stdout[:500]}")
except Exception as e:
    print(f"   ❌ Error testing ComfyUI: {e}")
print()

# 9. Summary
print("╔════════════════════════════════════════════════════════╗")
print("║                    SUMMARY                             ║")
print("╚════════════════════════════════════════════════════════╝")
print()

issues = []

# Check each requirement
if not all(os.path.exists(f) for f in files_to_check):
    issues.append("❌ Missing project files - Upload all 4 files to /root/comfyui-api/")

if not os.path.exists(comfyui_dir):
    issues.append("❌ ComfyUI not installed - Clone from GitHub")

if os.path.exists(models_dir):
    models = [f for f in os.listdir(models_dir) if f.endswith(('.safetensors', '.ckpt', '.pt'))]
    if not models:
        issues.append("❌ No AI models found - Download FLUX or other model")

try:
    import flask
except:
    issues.append("❌ Flask not installed - Run: pip install flask requests pyngrok")

if issues:
    print("🔧 ISSUES FOUND:")
    for issue in issues:
        print(f"   {issue}")
    print()
    print("💡 Fix these issues before running start_with_ngrok.py")
else:
    print("✅ ALL CHECKS PASSED!")
    print()
    print("🚀 You're ready to run:")
    print("   python start_with_ngrok.py")

print()
print("=" * 60)

