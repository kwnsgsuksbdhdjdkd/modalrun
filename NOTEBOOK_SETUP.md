# 🚀 Run ComfyUI API in Modal.com Notebooks

This guide shows you how to run the ComfyUI API **directly inside Modal.com notebooks**.

## 📦 What You Need

1. Modal.com account with notebooks access
2. This project folder uploaded to your notebook

## ✅ Step-by-Step Setup

### Step 1: Upload Files to Modal Notebook

1. Open your Modal notebook
2. Navigate to `/root/ComfyUI/custom_nodes/ComfyUI-Manager` (or create a new directory)
3. Upload these files:
   - `notebook_comfyui_api.py` (main API server)
   - `config.json` (already has your Discord webhook)
   - `workflows/flux_workflow.json` (optional, custom workflows)

**OR** create a fresh directory:

```bash
# In Modal notebook terminal:
cd /root
mkdir -p comfyui-api
cd comfyui-api

# Then upload the files here
```

### Step 2: Install Dependencies

In the notebook terminal:

```bash
pip install flask requests
```

### Step 3: Make Sure You Have Models

Check if you have models in ComfyUI:

```bash
ls /root/ComfyUI/models/checkpoints/
```

If empty, you need to download a model:

```bash
cd /root/ComfyUI/models/checkpoints/
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
```

⏰ This will take a few minutes (23GB download)

### Step 4: Run the API Server

```bash
python notebook_comfyui_api.py
```

**Output:**
```
🚀 Starting ComfyUI...
✅ ComfyUI is ready!
📬 Discord notification sent!
✅ API Server Started!

📡 Endpoints:
   POST http://localhost:5000/generate      - Generate images
   GET  http://localhost:5000/health        - Health check
   GET  http://localhost:5000/list-models   - List models
```

You'll also get a **Discord notification**! 🎉

### Step 5: Expose the API to Public (Modal Notebooks)

In Modal notebooks, you need to expose the port. Add this to your notebook:

**Option A: Using Modal's built-in port forwarding**

Modal notebooks should automatically expose ports. Check your notebook's URL and add `:5000` to access the API.

**Option B: Using ngrok (recommended for public access)**

```bash
# Install ngrok
pip install pyngrok

# Run ngrok in another terminal
ngrok http 5000
```

This will give you a public URL like: `https://abc123.ngrok.io`

### Step 6: Test the API

Once you have the URL (localhost or ngrok):

```bash
curl -X POST http://YOUR-URL/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful sunset over mountains"}' \
  --output test.png
```

**Or from Python:**

```python
import requests

response = requests.post(
    "http://YOUR-URL/generate",
    json={"prompt": "a cute cat wearing sunglasses"},
    timeout=300
)

with open("cat.png", "wb") as f:
    f.write(response.content)

print("✅ Image saved as cat.png")
```

## 🎨 Usage Examples

### Generate Image

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a futuristic city at night"}' \
  --output city.png
```

### Check Health

```bash
curl http://localhost:5000/health
```

### List Available Models

```bash
curl http://localhost:5000/list-models
```

## 🔧 Configuration

Edit the configuration at the top of `notebook_comfyui_api.py`:

```python
# Discord webhook (already set)
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/..."

# ComfyUI directory (default)
COMFYUI_DIR = "/root/ComfyUI"

# Ports
PORT = 8188        # ComfyUI port
API_PORT = 5000    # API server port
```

## 📁 File Structure in Modal Notebook

```
/root/
├── ComfyUI/                    # ComfyUI installation
│   ├── models/
│   │   └── checkpoints/
│   │       └── flux1-schnell.safetensors
│   └── ...
│
└── comfyui-api/               # Your project folder (paste here)
    ├── notebook_comfyui_api.py
    ├── config.json
    └── workflows/
        └── flux_workflow.json
```

## 🚀 Quick Start Script

Create a `start.sh` file:

```bash
#!/bin/bash

echo "🚀 Starting ComfyUI API..."

# Install dependencies
pip install flask requests -q

# Run the API
python notebook_comfyui_api.py
```

Make it executable and run:

```bash
chmod +x start.sh
./start.sh
```

## 🔒 Making it Public with ngrok

For a public URL that works from anywhere:

1. **Install pyngrok:**
   ```bash
   pip install pyngrok
   ```

2. **Create `start_with_ngrok.py`:**

```python
from pyngrok import ngrok
import subprocess
import time

# Start ngrok tunnel
public_url = ngrok.connect(5000)
print(f"🌍 Public URL: {public_url}")

# Start the API server
subprocess.Popen(["python", "notebook_comfyui_api.py"])

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Shutting down...")
```

3. **Run it:**
   ```bash
   python start_with_ngrok.py
   ```

## 🐛 Troubleshooting

### ComfyUI won't start

**Check if already running:**
```bash
ps aux | grep comfyui
# If running, kill it:
pkill -f "main.py"
```

**Check logs:**
```bash
tail -f /root/ComfyUI/comfyui.log
```

### Port already in use

```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port in the config
```

### Model not found

```bash
# Check models
ls -lh /root/ComfyUI/models/checkpoints/

# Download FLUX model if missing
cd /root/ComfyUI/models/checkpoints/
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
```

### Generation timeout

Edit `notebook_comfyui_api.py`:

```python
# Change max_wait to longer duration
max_wait = 600  # 10 minutes instead of 5
```

## 💡 Tips

1. **Keep it Running**: Modal notebooks may timeout if idle. Consider using Modal apps instead for production.

2. **Use Fast Models**: FLUX.1-schnell (4 steps) is much faster than FLUX.1-dev (50 steps)

3. **Monitor Resources**: Check GPU/RAM usage in Modal dashboard

4. **Save Your Work**: Modal notebooks can reset, so keep backups of your files

## 📚 Next Steps

- ✅ API is running in notebook
- 🎨 Customize workflows in `workflows/flux_workflow.json`
- 🤖 Integrate with Discord bot
- 🌐 Build a web frontend
- 📊 Add usage tracking

## 🆘 Need Help?

- Check Modal notebook logs
- Visit Modal documentation: https://modal.com/docs
- ComfyUI docs: https://github.com/comfyanonymous/ComfyUI

---

**Made with ❤️ for AI Art in Modal Notebooks**

