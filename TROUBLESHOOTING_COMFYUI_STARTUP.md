# 🔧 Troubleshooting: ComfyUI Won't Start

## Problem

ComfyUI fails to start in Modal notebook with error:
```
⏳ Waiting for ComfyUI... (30/30)
❌ ComfyUI failed to start
```

---

## 🔍 **Quick Diagnosis**

Run these commands in your Modal notebook to find the issue:

### Step 1: Check if ComfyUI is Installed

```bash
ls -la /root/ComfyUI/
ls -la /root/ComfyUI/main.py
```

**Expected:** Should see `main.py` and other ComfyUI files

**If missing:** ComfyUI is not installed!

---

### Step 2: Check if Python Dependencies are Installed

```bash
cd /root/ComfyUI
python main.py --help
```

**If you see errors about missing packages:** Dependencies not installed

---

### Step 3: Check if Port 8188 is Already in Use

```bash
lsof -i :8188
# OR
ps aux | grep main.py
```

**If something is listed:** Kill the existing process:
```bash
pkill -f "main.py"
```

---

### Step 4: Try Starting ComfyUI Manually

```bash
cd /root/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

**Look for error messages!** This will show you exactly why it's failing.

---

## ✅ **Solution 1: Install ComfyUI** (Most Common)

If ComfyUI is not installed or corrupted:

```bash
# Remove old installation (if exists)
rm -rf /root/ComfyUI

# Clone fresh copy
cd /root
git clone https://github.com/comfyanonymous/ComfyUI.git

# Install dependencies
cd /root/ComfyUI
pip install -r requirements.txt

# OR if using specific Python version:
pip3 install -r requirements.txt
```

**Wait for installation to complete** (~2-5 minutes)

---

## ✅ **Solution 2: Check Python Version**

ComfyUI requires **Python 3.10+**

```bash
python --version
# OR
python3 --version
```

**If Python < 3.10:**
```bash
# Modal notebooks usually have Python 3.10+
# If not, you may need to use a different Modal image
```

---

## ✅ **Solution 3: Install Missing Dependencies**

```bash
cd /root/ComfyUI

# Install PyTorch (required)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install ComfyUI requirements
pip install -r requirements.txt

# Install additional common dependencies
pip install accelerate transformers safetensors
```

---

## ✅ **Solution 4: Kill Existing ComfyUI Process**

If ComfyUI is already running in background:

```bash
# Find the process
ps aux | grep "main.py"

# Kill all ComfyUI processes
pkill -9 -f "main.py"

# Wait a moment
sleep 2

# Try starting again
cd /root/comfyui-api
python start_with_ngrok.py
```

---

## ✅ **Solution 5: Check Disk Space**

```bash
df -h
```

**If disk is full:** Free up space or increase Modal storage

---

## 🔧 **Complete Setup Script**

Run this in your Modal notebook to set up everything from scratch:

```bash
#!/bin/bash

echo "🔧 Complete ComfyUI Setup for Modal Notebook"
echo "============================================"

# Step 1: Check Python version
echo "1️⃣ Checking Python version..."
python --version

# Step 2: Install/Update ComfyUI
echo "2️⃣ Setting up ComfyUI..."
if [ ! -d "/root/ComfyUI" ]; then
    echo "   ComfyUI not found. Installing..."
    cd /root
    git clone https://github.com/comfyanonymous/ComfyUI.git
else
    echo "   ComfyUI found. Updating..."
    cd /root/ComfyUI
    git pull
fi

# Step 3: Install dependencies
echo "3️⃣ Installing dependencies..."
cd /root/ComfyUI
pip install -r requirements.txt -q

# Step 4: Install PyTorch
echo "4️⃣ Installing PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -q

# Step 5: Check if models directory exists
echo "5️⃣ Checking models directory..."
mkdir -p /root/ComfyUI/models/checkpoints
ls -lh /root/ComfyUI/models/checkpoints/

# Step 6: Test ComfyUI startup
echo "6️⃣ Testing ComfyUI startup..."
timeout 10 python /root/ComfyUI/main.py --listen 0.0.0.0 --port 8188 &
sleep 5
if lsof -i :8188 > /dev/null 2>&1; then
    echo "   ✅ ComfyUI started successfully!"
    pkill -f "main.py"
else
    echo "   ❌ ComfyUI failed to start. Check errors above."
fi

echo "============================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Download a model (if not already done)"
echo "2. Run: cd /root/comfyui-api && python start_with_ngrok.py"
```

**Save as:** `setup_comfyui.sh`

**Run:** `bash setup_comfyui.sh`

---

## 🎯 **Step-by-Step Manual Fix**

### Step 1: Clean Start

```bash
# Kill any existing processes
pkill -9 -f "main.py"
pkill -9 -f "notebook_comfyui_api.py"

# Wait
sleep 2
```

### Step 2: Check ComfyUI Installation

```bash
cd /root/ComfyUI
ls -la main.py
```

**If main.py doesn't exist:**
```bash
cd /root
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

### Step 3: Test ComfyUI Directly

```bash
cd /root/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

**Watch for errors!** Common ones:
- `ModuleNotFoundError: No module named 'torch'` → Install PyTorch
- `ModuleNotFoundError: No module named 'PIL'` → `pip install Pillow`
- `Address already in use` → Port 8188 is taken, kill the process

### Step 4: Once ComfyUI Starts Successfully

Press `Ctrl+C` to stop it, then:

```bash
cd /root/comfyui-api
python start_with_ngrok.py
```

---

## 📋 **Common Errors & Solutions**

### Error: `ModuleNotFoundError: No module named 'torch'`

**Fix:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Error: `ModuleNotFoundError: No module named 'accelerate'`

**Fix:**
```bash
pip install accelerate transformers safetensors
```

### Error: `Address already in use`

**Fix:**
```bash
pkill -9 -f "main.py"
sleep 2
# Try again
```

### Error: `Permission denied`

**Fix:**
```bash
chmod +x /root/ComfyUI/main.py
```

### Error: `CUDA out of memory`

**Fix:** Modal GPU issue. Try:
```bash
# Use CPU mode temporarily
python main.py --cpu
```

---

## 🔍 **Advanced Debugging**

### Check ComfyUI Logs

```bash
# Start ComfyUI with full output
cd /root/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 2>&1 | tee /tmp/comfyui.log

# In another terminal, check the log
tail -f /tmp/comfyui.log
```

### Check System Resources

```bash
# Check RAM
free -h

# Check GPU
nvidia-smi

# Check disk space
df -h

# Check processes
ps aux | grep python
```

### Verify Python Packages

```bash
pip list | grep -E "(torch|transformers|accelerate|safetensors|PIL)"
```

**Should see:**
- torch
- torchvision
- torchaudio
- transformers
- accelerate
- safetensors
- Pillow

---

## 🚀 **Quick Fix Script**

Copy and run this in Modal notebook:

```python
# quick_fix_comfyui.py
import subprocess
import os
import time

print("🔧 Quick Fix for ComfyUI Startup")
print("=" * 50)

# 1. Kill existing processes
print("1️⃣ Killing existing processes...")
subprocess.run(["pkill", "-9", "-f", "main.py"], stderr=subprocess.DEVNULL)
time.sleep(2)

# 2. Check if ComfyUI exists
comfyui_path = "/root/ComfyUI"
if not os.path.exists(f"{comfyui_path}/main.py"):
    print(f"2️⃣ ComfyUI not found. Installing...")
    os.chdir("/root")
    subprocess.run(["git", "clone", "https://github.com/comfyanonymous/ComfyUI.git"])
    os.chdir(comfyui_path)
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
else:
    print(f"2️⃣ ComfyUI found at {comfyui_path}")

# 3. Install PyTorch if needed
print("3️⃣ Checking PyTorch...")
try:
    import torch
    print(f"   ✅ PyTorch {torch.__version__} installed")
except ImportError:
    print("   Installing PyTorch...")
    subprocess.run([
        "pip", "install", "torch", "torchvision", "torchaudio",
        "--index-url", "https://download.pytorch.org/whl/cu118"
    ])

# 4. Test ComfyUI
print("4️⃣ Testing ComfyUI startup...")
os.chdir(comfyui_path)
process = subprocess.Popen(
    ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait 10 seconds and check
time.sleep(10)
if process.poll() is None:
    print("   ✅ ComfyUI started successfully!")
    process.terminate()
    time.sleep(1)
    process.kill()
    print("\n✅ Fix complete! Now run: python start_with_ngrok.py")
else:
    stdout, stderr = process.communicate()
    print("   ❌ ComfyUI failed to start!")
    print("\n📋 Error output:")
    print(stderr.decode()[-500:])  # Last 500 chars
    print("\n💡 Check the error above and install missing packages")

print("=" * 50)
```

**Run:** `python quick_fix_comfyui.py`

---

## ✅ **Prevention Checklist**

Before running `start_with_ngrok.py`:

- [ ] ComfyUI is installed: `ls /root/ComfyUI/main.py`
- [ ] Dependencies installed: `pip list | grep torch`
- [ ] No process on port 8188: `lsof -i :8188`
- [ ] Sufficient disk space: `df -h`
- [ ] Python 3.10+: `python --version`
- [ ] Can start manually: `cd /root/ComfyUI && timeout 5 python main.py`

---

## 🆘 **Still Not Working?**

### Get the Actual Error

```bash
cd /root/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

**Send me the error message!** Look for:
- Red error text
- `Traceback` lines
- `ModuleNotFoundError`
- `ImportError`
- `RuntimeError`

---

## 📝 **Summary**

| Issue | Quick Fix |
|-------|-----------|
| ComfyUI not installed | `git clone` then `pip install -r requirements.txt` |
| Missing dependencies | `pip install torch torchvision` |
| Port in use | `pkill -9 -f "main.py"` |
| Python version | Check `python --version` (need 3.10+) |
| Disk full | Free up space or increase Modal storage |

---

**Most common fix:** ComfyUI or its dependencies are not properly installed in Modal.

**Run the complete setup script above** and it should work! 🚀
