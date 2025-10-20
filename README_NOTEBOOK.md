# 🎨 ComfyUI API for Modal Notebooks

**Run ComfyUI API directly inside Modal.com notebooks with a public URL!**

This is a **notebook-ready version** of the ComfyUI API that you can simply paste into your Modal notebook environment and run. Perfect for quick deployment without local setup.

---

## 🚀 Quick Start (3 Steps)

### 1️⃣ Upload Files to Modal Notebook

Create a directory in your Modal notebook:

```bash
cd /root
mkdir comfyui-api
cd comfyui-api
```

Upload these files to this directory:
- ✅ `notebook_comfyui_api.py` (main API server)
- ✅ `start_with_ngrok.py` (for public URL)
- ✅ `config.json` (optional, for Discord notifications)
- ✅ `NOTEBOOK_SETUP.md` (instructions)

### 2️⃣ Run Setup Script

```bash
chmod +x notebook_setup.sh
./notebook_setup.sh
```

This will:
- ✅ Install dependencies (Flask, requests, pyngrok)
- ✅ Check for models
- ✅ Set up project structure
- ✅ Verify everything is ready

### 3️⃣ Start the API with Public URL

```bash
python start_with_ngrok.py
```

**Output:**
```
╔════════════════════════════════════════════════════════╗
║  🌍 ComfyUI API with Public URL (ngrok)               ║
╚════════════════════════════════════════════════════════╝

✅ ngrok tunnel created!
🌍 PUBLIC URL: https://abc123.ngrok-free.app

📡 API Endpoints:
   POST https://abc123.ngrok-free.app/generate
   GET  https://abc123.ngrok-free.app/health

✅ Discord notification sent!
🎉 Everything is running!
```

**That's it!** Your API is live with a public URL! 🎉

---

## 📖 What This Does

1. ✅ Starts ComfyUI in your Modal notebook
2. ✅ Creates a REST API wrapper around ComfyUI
3. ✅ Exposes public HTTPS endpoint via ngrok
4. ✅ Sends Discord notification with your URL
5. ✅ Handles image generation requests
6. ✅ Returns generated PNG images

---

## 🎯 Usage Examples

### Generate an Image

```bash
curl -X POST https://YOUR-URL.ngrok-free.app/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful sunset over mountains"}' \
  --output sunset.png
```

### Using Python

```python
import requests

# Generate image
response = requests.post(
    "https://YOUR-URL.ngrok-free.app/generate",
    json={"prompt": "a cute cat wearing sunglasses"},
    timeout=300
)

# Save image
with open("cat.png", "wb") as f:
    f.write(response.content)

print("✅ Image saved!")
```

### Check API Health

```bash
curl https://YOUR-URL.ngrok-free.app/health
```

### List Available Models

```bash
curl https://YOUR-URL.ngrok-free.app/list-models
```

---

## 📁 Files Included

| File | Description |
|------|-------------|
| `notebook_comfyui_api.py` | Main API server (Flask app) |
| `start_with_ngrok.py` | Launcher with ngrok for public URL |
| `notebook_setup.sh` | Automated setup script |
| `config.json` | Configuration (Discord webhook) |
| `NOTEBOOK_SETUP.md` | Detailed setup instructions |
| `README_NOTEBOOK.md` | This file |

---

## ⚙️ Configuration

### Discord Webhook

Your Discord webhook is already configured in:
- `config.json`
- `notebook_comfyui_api.py`
- `start_with_ngrok.py`

To change it, edit the `DISCORD_WEBHOOK` variable in any of these files.

### Custom Workflow

Edit the `DEFAULT_WORKFLOW` in `notebook_comfyui_api.py` or pass a custom workflow in your API request:

```python
import requests
import json

# Load your custom workflow
with open("my_workflow.json") as f:
    workflow = json.load(f)

# Generate with custom workflow
response = requests.post(
    "https://YOUR-URL/generate",
    json={
        "prompt": "your prompt",
        "workflow": workflow
    }
)
```

### Change Model

Edit `DEFAULT_WORKFLOW` in `notebook_comfyui_api.py`:

```python
"4": {
    "inputs": {
        "ckpt_name": "your-model-name.safetensors"  # Change this
    },
    "class_type": "CheckpointLoaderSimple"
}
```

---

## 🐛 Troubleshooting

### Problem: "ComfyUI failed to start"

**Solution:**
```bash
# Check if ComfyUI is already running
ps aux | grep comfyui

# Kill existing process
pkill -f "main.py"

# Try again
python start_with_ngrok.py
```

### Problem: "Model not found"

**Solution:**
```bash
# Check models directory
ls /root/ComfyUI/models/checkpoints/

# Download FLUX model
cd /root/ComfyUI/models/checkpoints/
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
```

### Problem: "Port already in use"

**Solution:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 8188
lsof -ti:8188 | xargs kill -9

# Try again
python start_with_ngrok.py
```

### Problem: "ngrok tunnel failed"

**Solution:**
```bash
# Kill all ngrok processes
pkill -9 ngrok

# Wait a moment
sleep 2

# Try again
python start_with_ngrok.py
```

### Problem: "Generation timeout"

**Solution:** Edit `notebook_comfyui_api.py`:

```python
# Line ~150, change max_wait
max_wait = 600  # Increase from 300 to 600 seconds
```

---

## 💡 Tips & Best Practices

### 1. Use Fast Models
- ✅ FLUX.1-schnell: 4 steps, ~20-30 seconds
- ❌ FLUX.1-dev: 50 steps, ~3-5 minutes

### 2. Keep Models Downloaded
Pre-download models to avoid delays:

```bash
cd /root/ComfyUI/models/checkpoints/
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
```

### 3. Monitor Resources
Modal notebooks have resource limits. Check usage in the dashboard.

### 4. Save Your Work
Modal notebooks can reset. Keep backups of:
- Custom workflows
- Configuration files
- Generated images (download them!)

### 5. Use ngrok for Testing
For production, consider deploying as a proper Modal app (see main README).

---

## 🔄 Comparison: Notebook vs. App Deployment

| Feature | Notebook Version | App Deployment |
|---------|------------------|----------------|
| **Setup** | Copy files, run script | Deploy with Modal CLI |
| **URL** | ngrok (temporary) | Permanent Modal URL |
| **Scaling** | Single instance | Auto-scaling |
| **Cost** | Notebook hours | Pay per request |
| **Reliability** | Manual restart needed | Auto-restart |
| **Best For** | Testing, development | Production use |

**Use notebook version for:** Quick testing, development, learning

**Use app deployment for:** Production, public APIs, scaling

---

## 📚 Next Steps

- ✅ **You're ready!** API is running
- 🎨 Customize workflows for different styles
- 🤖 Integrate with Discord bot
- 🌐 Build a web frontend
- 📊 Add usage analytics
- 🔐 Add authentication for security

---

## 🆘 Need Help?

1. **Check logs:** Look at the terminal output
2. **Read detailed guide:** See `NOTEBOOK_SETUP.md`
3. **Modal docs:** https://modal.com/docs
4. **ComfyUI docs:** https://github.com/comfyanonymous/ComfyUI

---

## 📞 Support

- Modal Discord: https://discord.gg/modal
- ComfyUI Community: https://github.com/comfyanonymous/ComfyUI/discussions

---

## 🎉 You're All Set!

Your ComfyUI API is running in Modal notebooks with a public URL!

**Check your Discord** for the URL notification 📬

**Start generating:** Use the examples above 🎨

---

**Made with ❤️ for the AI Art community**

**Happy Creating! 🚀**

