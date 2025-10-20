# 🎨 ComfyUI API for Modal Notebooks

**Run ComfyUI with a public API directly inside Modal.com notebooks!**

Generate AI images using FLUX and other models with a simple REST API - no complex setup required.

---

## 🚀 Quick Start

### Step 1: Upload to Modal Notebook

Upload these files to your Modal.com notebook (e.g., `/root/comfyui-api/`):

```
✅ notebook_comfyui_api.py      - Main API server
✅ start_with_ngrok.py          - Public URL launcher  
✅ notebook_setup.sh            - Setup script
✅ config.json                  - Your Discord webhook (pre-configured!)
```

### Step 2: Run Setup

```bash
cd /root/comfyui-api
bash notebook_setup.sh
```

### Step 3: Start API with Public URL

```bash
python start_with_ngrok.py
```

**Output:**
```
✅ ngrok tunnel created!
🌍 PUBLIC URL: https://abc123.ngrok-free.app
📬 Discord notification sent!
🎉 Everything is running!
```

**Check your Discord** - you'll get a notification with your API URL! 📬

---

## 🎯 Generate Your First Image

```bash
curl -X POST https://YOUR-URL/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful sunset over mountains"}' \
  --output sunset.png
```

**Using Python:**

```python
import requests

response = requests.post(
    "https://YOUR-URL/generate",
    json={"prompt": "a cute cat wearing sunglasses"},
    timeout=300
)

with open("cat.png", "wb") as f:
        f.write(response.content)

print("✅ Image saved!")
```

---

## 📁 Project Files

| File | Description |
|------|-------------|
| `notebook_comfyui_api.py` | Main API server (Flask app) |
| `start_with_ngrok.py` | Public URL launcher with ngrok |
| `notebook_setup.sh` | Automated setup script |
| `config.json` | Configuration (Discord webhook pre-configured) |
| `models_guide.md` | Guide for downloading and managing models |
| `README_NOTEBOOK.md` | Full documentation |
| `NOTEBOOK_SETUP.md` | Detailed setup instructions |
| `NOTEBOOK_QUICK_START.txt` | Quick reference guide |

---

## 📚 Documentation

- **Quick Start:** [NOTEBOOK_QUICK_START.txt](NOTEBOOK_QUICK_START.txt)
- **Full Guide:** [README_NOTEBOOK.md](README_NOTEBOOK.md)
- **Setup Details:** [NOTEBOOK_SETUP.md](NOTEBOOK_SETUP.md)
- **Models Guide:** [models_guide.md](models_guide.md)

---

## ✨ Features

- ✅ **Easy Setup** - Just 3 commands to get started
- ✅ **Public URL** - Access from anywhere via ngrok
- ✅ **Discord Notifications** - Get URL sent to Discord
- ✅ **Auto Setup** - Downloads models if needed
- ✅ **REST API** - Simple JSON requests
- ✅ **Multiple Models** - FLUX, Stable Diffusion, etc.
- ✅ **Custom Workflows** - Use your own ComfyUI workflows

---

## 🎨 API Endpoints

### `POST /generate`
Generate an image from a text prompt

**Request:**
```json
{
  "prompt": "a beautiful landscape",
  "workflow": {...}  // optional
}
```

**Response:** PNG image

### `GET /health`
Check API health status

**Response:**
```json
{
  "status": "healthy",
  "comfyui": "running"
}
```

### `GET /list-models`
List available models

**Response:**
```json
{
  "models": ["flux1-schnell.safetensors", ...]
}
```

---

## ⚙️ Configuration

Your Discord webhook is already configured in:
- `config.json`
- `notebook_comfyui_api.py`
- `start_with_ngrok.py`

**Discord Webhook:**
```
https://discord.com/api/webhooks/1429488694498295899/soU4ivZA_...
```

To change it, edit the `DISCORD_WEBHOOK` variable in the files above.

---

## 🔧 Requirements

- Modal.com notebook with ComfyUI installed
- At least one model in `/root/ComfyUI/models/checkpoints/`
- Python 3.8+

The setup script will install:
- Flask (API server)
- requests (HTTP client)
- pyngrok (public URL tunneling)

---

## 🐛 Troubleshooting

### "ComfyUI failed to start"
```bash
pkill -f "main.py"  # Kill existing process
python start_with_ngrok.py  # Try again
```

### "Model not found"
```bash
# Check models
ls /root/ComfyUI/models/checkpoints/

# Download FLUX
cd /root/ComfyUI/models/checkpoints/
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
```

### "Port already in use"
```bash
lsof -ti:5000 | xargs kill -9
lsof -ti:8188 | xargs kill -9
```

See [NOTEBOOK_SETUP.md](NOTEBOOK_SETUP.md) for more troubleshooting.

---

## 💡 Tips

1. **Use Fast Models:** FLUX.1-schnell (4 steps) is much faster than FLUX.1-dev (50 steps)
2. **Pre-download Models:** Download before starting to avoid delays
3. **Monitor Resources:** Check Modal dashboard for usage
4. **Save Generated Images:** Download them before notebook resets

---

## 📦 What This Does

1. ✅ Starts ComfyUI in your Modal notebook
2. ✅ Creates a REST API wrapper (Flask)
3. ✅ Exposes public HTTPS endpoint (ngrok)
4. ✅ Sends Discord notification with URL
5. ✅ Handles image generation requests
6. ✅ Returns generated PNG images

---

## 🎉 You're Ready!

**Upload the files to your Modal notebook and run:**

```bash
cd /root/comfyui-api
python start_with_ngrok.py
```

**Your API will be live in ~30 seconds!**

**Check Discord for your public URL! 📬**

---

## 🆘 Need Help?

1. Read [NOTEBOOK_QUICK_START.txt](NOTEBOOK_QUICK_START.txt)
2. See [NOTEBOOK_SETUP.md](NOTEBOOK_SETUP.md) for details
3. Check [models_guide.md](models_guide.md) for model info
4. Visit Modal docs: https://modal.com/docs
5. ComfyUI docs: https://github.com/comfyanonymous/ComfyUI

---

**Made with ❤️ for the AI Art community**

**Happy Creating! 🚀**

