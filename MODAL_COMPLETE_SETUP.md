# 🚀 Complete Setup Guide for Modal Notebooks

## ⚠️ IMPORTANT: You're Running OLD Files!

Your **local files** (Windows) are updated, but Modal is running **old versions**.

You need to **RE-UPLOAD** the updated files to Modal!

---

## 📦 Step 1: Upload ALL Files to Modal

### **Files to Upload:**

From your Windows folder: `C:\Users\Nesar\Documents\modalexe\`

Upload these **5 files** to Modal at `/root/comfyui-api/`:

1. ✅ `notebook_comfyui_api.py` (updated)
2. ✅ `start_with_ngrok.py` (updated - fixes URL display)
3. ✅ `config.json` (your Discord webhook)
4. ✅ `notebook_setup.sh` (setup script)
5. ✅ `diagnose_modal.py` (NEW - diagnostic tool)

### **How to Upload in Modal:**

**Option A: Using Modal's File Upload**
1. Open Modal notebook
2. Navigate to `/root/comfyui-api/` directory
3. Use the file upload button/feature
4. Upload each file

**Option B: Using Terminal Commands**
1. Open Modal notebook terminal
2. Run for each file:
```bash
cd /root/comfyui-api
# Then upload via Modal's interface or use nano to paste content
```

---

## 🔍 Step 2: Run Diagnostics

Before trying to start the API, run the diagnostic script:

### **In Jupyter Cell:**
```python
!cd /root/comfyui-api && python diagnose_modal.py
```

### **Or in Terminal:**
```bash
cd /root/comfyui-api
python diagnose_modal.py
```

**This will check:**
- ✅ Python version
- ✅ Project files present
- ✅ ComfyUI installed
- ✅ AI models available
- ✅ Dependencies installed
- ✅ Ports available
- ✅ ComfyUI can start

**Fix any issues it reports before continuing!**

---

## 🛠️ Step 3: Fix Common Issues

### **Issue A: ComfyUI Not Installed**

```bash
cd /root
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

### **Issue B: No AI Models**

```bash
mkdir -p /root/ComfyUI/models/checkpoints
cd /root/ComfyUI/models/checkpoints

# Download FLUX (this takes 5-10 minutes, 23GB)
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
```

### **Issue C: Missing Dependencies**

```bash
pip install flask requests pyngrok torch torchvision
```

### **Issue D: Ports in Use**

```bash
# Kill any existing processes
pkill -f "main.py"
pkill -9 ngrok

# Wait a moment
sleep 2
```

---

## 🚀 Step 4: Start the API

### **In Jupyter Cell:**
```python
!cd /root/comfyui-api && python start_with_ngrok.py
```

### **Or in Terminal:**
```bash
cd /root/comfyui-api
python start_with_ngrok.py
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════╗
║  🌍 ComfyUI API with Public URL (ngrok)               ║
╚════════════════════════════════════════════════════════╝

🔑 Configuring ngrok authentication...
✅ ngrok authenticated!
🔗 Creating ngrok tunnel on port 5000...
✅ ngrok tunnel created!

============================================================
🌍 PUBLIC URL: https://abc123.ngrok-free.dev
============================================================

📡 API Endpoints:
   POST https://abc123.ngrok-free.dev/generate
   GET  https://abc123.ngrok-free.dev/health

✅ Discord notification sent!
🚀 Starting ComfyUI API server...
✅ API Server started!
```

**Check your Discord for the URL!** 📬

---

## 🎨 Step 5: Test the API

### **Test 1: Health Check**

```python
import requests

response = requests.get("https://YOUR-URL.ngrok-free.dev/health")
print(response.json())
```

Expected: `{"status": "healthy", "comfyui": "running"}`

### **Test 2: Generate Image**

```python
import requests

response = requests.post(
    "https://YOUR-URL.ngrok-free.dev/generate",
    json={"prompt": "a beautiful sunset over mountains"},
    timeout=300
)

if response.status_code == 200:
    with open("sunset.png", "wb") as f:
        f.write(response.content)
    print("✅ Image saved as sunset.png!")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
```

---

## 🔧 Troubleshooting

### **Still showing "NgrokTunnel: ..." in URL?**

**Problem:** You're running the OLD `start_with_ngrok.py` file.

**Solution:** 
1. Delete the old file in Modal
2. Upload the NEW version from your Windows folder
3. Verify it uploaded correctly:
```bash
grep "tunnel.public_url" /root/comfyui-api/start_with_ngrok.py
```

Should show: `public_url = tunnel.public_url`

### **ComfyUI Won't Start?**

**Check logs:**
```bash
cd /root/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

Look for error messages!

Common errors:
- `ModuleNotFoundError: No module named 'torch'` → Install: `pip install torch torchvision`
- `No checkpoints found` → Download a model (see Issue B above)
- `Address already in use` → Kill existing process: `pkill -f "main.py"`

### **Connection Refused Error?**

This means Flask API didn't start because ComfyUI didn't start.

**Fix ComfyUI first:**
1. Run diagnostics: `python diagnose_modal.py`
2. Fix any issues it reports
3. Test ComfyUI manually: `cd /root/ComfyUI && python main.py --listen 0.0.0.0 --port 8188`
4. If ComfyUI starts successfully, press Ctrl+C and run your wrapper again

---

## ✅ Final Checklist

Before running `start_with_ngrok.py`, ensure:

- [ ] All 5 files uploaded to `/root/comfyui-api/`
- [ ] ComfyUI installed at `/root/ComfyUI/`
- [ ] At least one model in `/root/ComfyUI/models/checkpoints/`
- [ ] Dependencies installed (`flask`, `requests`, `pyngrok`, `torch`)
- [ ] Ports 5000 and 8188 are free
- [ ] Diagnostic script passes all checks

---

## 📋 Quick Commands Reference

| Task | Command |
|------|---------|
| Navigate to project | `cd /root/comfyui-api` |
| Run diagnostics | `python diagnose_modal.py` |
| Start API | `python start_with_ngrok.py` |
| Check files | `ls -la` |
| Check ComfyUI | `ls /root/ComfyUI` |
| Check models | `ls /root/ComfyUI/models/checkpoints/` |
| Kill processes | `pkill -f "main.py" && pkill -9 ngrok` |
| Test ComfyUI | `cd /root/ComfyUI && python main.py --listen 0.0.0.0 --port 8188` |

---

## 🎯 What You Should Do NOW

1. **Upload the updated files** to Modal
2. **Run diagnostics**: `python diagnose_modal.py`
3. **Fix any issues** it reports
4. **Start the API**: `python start_with_ngrok.py`
5. **Check Discord** for your public URL
6. **Test** with a simple request

---

**Need Help?** Share the output of `diagnose_modal.py` and I can tell you exactly what to fix! 🚀

