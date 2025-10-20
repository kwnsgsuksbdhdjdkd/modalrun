# 📓 Running in Jupyter/Modal Notebooks

## Important: Shell Commands in Jupyter

In Jupyter notebooks (including Modal notebooks), **shell commands need the `!` prefix**.

### ❌ Wrong (Python cell):
```python
ngrok config add-authtoken YOUR_TOKEN
cd /root/comfyui-api
python start_with_ngrok.py
```

### ✅ Correct (Jupyter cell):
```python
!ngrok config add-authtoken YOUR_TOKEN
!cd /root/comfyui-api
!python start_with_ngrok.py
```

---

## 🚀 **Updated: No Manual Token Configuration Needed!**

**Good news!** The `start_with_ngrok.py` file now **automatically configures your ngrok token** for you. You don't need to run the `ngrok config` command separately anymore!

Your token is already saved in the script: `34I1jdUho1Jn8wo1QaRkocbxPkP_5bUtZxmGAGkVdtvctTDrb`

---

## 📋 **Complete Setup in Jupyter Notebook**

### **Cell 1: Navigate and Install Dependencies**

```python
!cd /root/comfyui-api && pip install flask requests pyngrok
```

### **Cell 2: Upload Files**

Upload these 4 files to `/root/comfyui-api/`:
- `notebook_comfyui_api.py`
- `start_with_ngrok.py` (updated version with token)
- `notebook_setup.sh`
- `config.json`

### **Cell 3: Start the API**

```python
!cd /root/comfyui-api && python start_with_ngrok.py
```

**That's it!** The script will:
1. ✅ Auto-configure ngrok with your token
2. ✅ Create public tunnel
3. ✅ Start ComfyUI in background
4. ✅ Start Flask API
5. ✅ Send Discord notification

---

## 🎨 **Test the API (New Cell)**

```python
import requests

# Your public URL (replace with actual URL from output)
API_URL = "https://YOUR-URL.ngrok-free.app"

# Generate an image
response = requests.post(
    f"{API_URL}/generate",
    json={"prompt": "a beautiful sunset over mountains"},
    timeout=300
)

# Save the image
if response.status_code == 200:
    with open("sunset.png", "wb") as f:
        f.write(response.content)
    print("✅ Image saved as sunset.png")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
```

---

## 🔧 **Common Issues in Jupyter**

### **Issue: Syntax Error with Shell Commands**

**Error:**
```
SyntaxError: invalid decimal literal
```

**Fix:** Add `!` prefix to shell commands in Jupyter cells.

### **Issue: Cell Hangs / Doesn't Return**

**Reason:** The API server runs continuously.

**Fix:** 
- Option 1: Run in background: `!cd /root/comfyui-api && python start_with_ngrok.py &`
- Option 2: Run in a separate terminal in Modal
- Option 3: Use Jupyter's terminal feature

### **Issue: ComfyUI Not Starting**

**Check if ComfyUI exists:**
```python
!ls -la /root/ComfyUI
```

**Install if missing:**
```python
!cd /root && git clone https://github.com/comfyanonymous/ComfyUI.git
!cd /root/ComfyUI && pip install -r requirements.txt
```

**Download model:**
```python
!mkdir -p /root/ComfyUI/models/checkpoints
!cd /root/ComfyUI/models/checkpoints && wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
```

---

## 📱 **Running in Background**

To keep the API running while using other notebook cells:

```python
import subprocess

# Start in background
process = subprocess.Popen(
    ["python", "start_with_ngrok.py"],
    cwd="/root/comfyui-api",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print("✅ API started in background!")
print("Check Discord for your public URL")
```

**To stop later:**
```python
process.terminate()
print("✅ API stopped")
```

---

## 🎯 **Quick Reference**

| Task | Command (in Jupyter cell) |
|------|--------------------------|
| Navigate to project | `!cd /root/comfyui-api` |
| Install dependencies | `!pip install flask requests pyngrok` |
| Start API | `!python start_with_ngrok.py` |
| Check ComfyUI | `!ls /root/ComfyUI` |
| Check models | `!ls /root/ComfyUI/models/checkpoints/` |
| Kill processes | `!pkill -f "main.py"` |
| View logs | `!tail -f /root/ComfyUI/comfyui.log` |

---

## ✅ **Updated Files**

The following files have been updated to work better in Jupyter notebooks:

1. **`start_with_ngrok.py`**
   - ✅ Auto-configures ngrok token
   - ✅ Cleaner URL display
   - ✅ Better error messages

2. **`notebook_comfyui_api.py`**
   - ✅ No changes needed

3. **`config.json`**
   - ✅ Discord webhook pre-configured

---

## 🆘 **Need Help?**

1. Check if all files are uploaded: `!ls /root/comfyui-api`
2. Check if ComfyUI is installed: `!ls /root/ComfyUI`
3. Check if models exist: `!ls /root/ComfyUI/models/checkpoints/`
4. View this guide: `JUPYTER_NOTEBOOK_INSTRUCTIONS.md`

---

**Made with ❤️ for Jupyter/Modal notebooks**

