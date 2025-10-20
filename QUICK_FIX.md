# 🚨 QUICK FIX: Image Generation Timeout

## Your Error
```
⏱️  Generation took 300.6 seconds
📊 Image info: None
❌ Generation timeout or failed!
```

## Most Likely Cause
**The model file doesn't exist or has the wrong name.**

---

## ✅ Solution (3 Steps)

### Step 1: Upload Updated Files to Modal Notebook

Upload these 2 files to `/root/comfyui-api/`:

1. **`notebook_comfyui_api.py`** (UPDATED - model name fixed)
2. **`check_comfyui_errors.py`** (NEW - diagnostic tool)

### Step 2: Check if Model Exists

In your Modal notebook, run:

```bash
cd /root/comfyui-api
python check_comfyui_errors.py
```

**If you see:**
```
❌ No models found in checkpoints directory!
```

**Then download the model:**
```bash
cd /root/ComfyUI/models/checkpoints/
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
```

⏰ **This takes 5-10 minutes** (23GB file)

### Step 3: Restart the API

```bash
cd /root/comfyui-api
pkill -f "main.py"
python start_with_ngrok.py
```

---

## 🎯 Test Again

```bash
curl -X POST YOUR-NGROK-URL/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a cute cat wearing sunglasses"}' \
  --output cat.png
```

---

## What Was Fixed

### 1. Model Name Mismatch ❌ → ✅
```python
# OLD (Wrong):
"ckpt_name": "flux1-krea-dev.safetensors"  # ❌

# NEW (Correct):
"ckpt_name": "flux1-schnell.safetensors"  # ✅
```

### 2. Better Error Logging ✅
The updated API now shows:
- ComfyUI execution errors
- Error messages from ComfyUI
- Last known status on timeout

### 3. Diagnostic Tool ✅
New `check_comfyui_errors.py` checks:
- ComfyUI running status
- Available models
- Queue status
- Specific request errors

---

## If Still Not Working

Run this to see the actual error:

```bash
python check_comfyui_errors.py YOUR_PROMPT_ID
```

Example:
```bash
python check_comfyui_errors.py 55c7cb34-0905-4557-b877-50e9fccd56cd
```

See **TROUBLESHOOTING_GENERATION_TIMEOUT.md** for detailed debugging steps.

---

## Files Changed

- ✅ `notebook_comfyui_api.py` - Line 57: Model name fixed
- ✅ `notebook_comfyui_api.py` - Enhanced error logging in `wait_for_completion()`
- ✅ `check_comfyui_errors.py` - NEW diagnostic tool
- ✅ `TROUBLESHOOTING_GENERATION_TIMEOUT.md` - NEW detailed guide

---

**Need Help?** Read TROUBLESHOOTING_GENERATION_TIMEOUT.md
