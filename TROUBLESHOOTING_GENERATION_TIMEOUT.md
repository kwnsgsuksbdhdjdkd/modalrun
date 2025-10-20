# 🔧 Troubleshooting: Image Generation Timeout

## Problem

Image generation requests timeout after 300 seconds with error:
```
⏱️  Generation took 300.6 seconds
📊 Image info: None
❌ Generation timeout or failed!
```

---

## Quick Diagnosis (Run This First!)

Upload and run the diagnostic script in your Modal notebook:

```bash
python check_comfyui_errors.py 55c7cb34-0905-4557-b877-50e9fccd56cd
```
*(Replace with your actual prompt_id from the error logs)*

This will show you:
- ✅ ComfyUI status
- ✅ Available models
- ✅ Queue status
- ✅ Error details for your specific request

---

## Common Causes & Solutions

### 1. ❌ Model Not Found (Most Common)

**Symptoms:**
- Timeout after 300 seconds
- No error message in API logs
- ComfyUI silently fails

**Check:**
```bash
# List available models
ls -lh /root/ComfyUI/models/checkpoints/

# Or use the API
curl http://localhost:5000/list-models
```

**Fix:**
```bash
# Download FLUX.1-schnell model (23GB, ~5-10 minutes)
cd /root/ComfyUI/models/checkpoints/
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors

# Verify download
ls -lh flux1-schnell.safetensors
```

**Expected output:** File should be ~23GB (23,805,974,864 bytes)

---

### 2. ❌ Model Name Mismatch

**Symptoms:**
- Model exists but generation fails
- ComfyUI logs show "checkpoint not found"

**Check workflow configuration:**
```python
# In notebook_comfyui_api.py, check line 57:
"ckpt_name": "flux1-schnell.safetensors"  # ✅ Correct

# NOT:
"ckpt_name": "flux1-krea-dev.safetensors"  # ❌ Wrong
```

**Fix:**
1. Download the updated `notebook_comfyui_api.py` from this repo (already fixed)
2. Or manually edit line 57 to match your model name

---

### 3. ❌ ComfyUI Crashed or Not Running

**Check:**
```bash
# Check if ComfyUI is running
ps aux | grep "main.py"

# Check ComfyUI health
curl http://localhost:8188/system_stats
```

**If not running:**
```bash
# Kill any stuck processes
pkill -f "main.py"

# Restart the API
python start_with_ngrok.py
```

---

### 4. ❌ GPU Out of Memory

**Symptoms:**
- ComfyUI crashes during generation
- No image produced after 300 seconds
- Modal logs show CUDA errors

**Check GPU usage:**
```bash
# In Modal notebook
!nvidia-smi
```

**Fix:**
- Use smaller image size (512x512 instead of 1024x1024)
- Reduce batch size
- Use FLUX.1-schnell (4 steps) instead of FLUX.1-dev (50 steps)

**Modify request:**
```python
# Smaller image size
{
  "prompt": "your prompt",
  "workflow": {
    ...
    "5": {
      "inputs": {
        "width": 512,    # Reduced from 1024
        "height": 512,   # Reduced from 1024
        "batch_size": 1
      },
      "class_type": "EmptyLatentImage"
    }
  }
}
```

---

### 5. ❌ ComfyUI Queue Stuck

**Check queue:**
```bash
curl http://localhost:8188/queue
```

**Clear stuck tasks:**
```bash
# Interrupt current execution
curl -X POST http://localhost:8188/interrupt

# Clear queue
curl -X POST http://localhost:8188/queue \
  -H "Content-Type: application/json" \
  -d '{"clear": true}'
```

---

## Step-by-Step Debugging

### Step 1: Run Diagnostic Script

```bash
python check_comfyui_errors.py
```

This checks:
- ComfyUI running status
- Available models
- Queue status
- Recent errors

### Step 2: Check Your Specific Request

If you have a prompt_id from the error:
```bash
python check_comfyui_errors.py YOUR_PROMPT_ID
```

Example:
```bash
python check_comfyui_errors.py 55c7cb34-0905-4557-b877-50e9fccd56cd
```

### Step 3: Manual History Check

```bash
# Check ComfyUI history for your prompt
curl http://localhost:8188/history/YOUR_PROMPT_ID | python -m json.tool
```

Look for:
- `"status_str": "error"` - Indicates execution error
- `"messages"` - Error messages from ComfyUI
- `"outputs"` - Should contain image data if successful

### Step 4: Test with Simple Workflow

```bash
# Test just loading the model (no generation)
curl -X POST http://localhost:8188/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": {
      "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
          "ckpt_name": "flux1-schnell.safetensors"
        }
      }
    },
    "client_id": "test"
  }'
```

If this fails, the model doesn't exist or name is wrong.

---

## Enhanced Error Logging

The updated `notebook_comfyui_api.py` now includes:

✅ **Detailed error detection** - Shows ComfyUI execution errors  
✅ **Status logging** - Reports ComfyUI messages  
✅ **Timeout diagnostics** - Shows last known status on timeout  

**Example enhanced output:**
```
❌ ComfyUI execution error detected!
   Error details: {
     "status_str": "error",
     "completed": false,
     "messages": [
       ["Error loading checkpoint: file not found"]
     ]
   }
```

---

## Files to Update

After cloning this repo, replace these files in your Modal notebook:

1. **`notebook_comfyui_api.py`** - Fixed model name + enhanced logging
2. **`check_comfyui_errors.py`** - New diagnostic tool

```bash
# In Modal notebook
cd /root/comfyui-api

# Download updated files
# (Upload from your local copy or use git pull)

# Restart the API
pkill -f "main.py"
pkill -f "notebook_comfyui_api.py"
python start_with_ngrok.py
```

---

## Prevention Checklist

Before running image generation:

- [ ] ComfyUI is running (`curl http://localhost:8188/system_stats`)
- [ ] Model exists (`ls /root/ComfyUI/models/checkpoints/*.safetensors`)
- [ ] Model name in code matches file name
- [ ] Sufficient GPU memory available
- [ ] No stuck tasks in queue (`curl http://localhost:8188/queue`)

---

## Still Not Working?

### Get ComfyUI Console Output

ComfyUI may be logging errors that aren't visible through the API:

```bash
# In Modal notebook, check ComfyUI process
ps aux | grep main.py

# If you started ComfyUI manually, check its console output
# Look for red error messages about:
# - File not found
# - CUDA out of memory
# - Model loading errors
```

### Test Directly with ComfyUI

Bypass the Flask API and test ComfyUI directly:

```bash
# Queue directly to ComfyUI
curl -X POST http://localhost:8188/prompt \
  -H "Content-Type: application/json" \
  -d @workflows/flux_workflow.json
```

### Check Modal Notebook Resources

```bash
# Check disk space
df -h

# Check memory
free -h

# Check GPU
nvidia-smi
```

---

## Get Help

If you're still stuck:

1. **Run diagnostic:** `python check_comfyui_errors.py YOUR_PROMPT_ID`
2. **Check logs:** Look for error messages in Modal notebook console
3. **Verify model:** Ensure `flux1-schnell.safetensors` exists and is complete (23GB)
4. **Restart everything:** Kill all processes and run `python start_with_ngrok.py`

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python check_comfyui_errors.py` | Run full diagnostic |
| `python check_comfyui_errors.py PROMPT_ID` | Check specific request |
| `curl http://localhost:8188/system_stats` | Check ComfyUI health |
| `curl http://localhost:8188/queue` | Check queue status |
| `curl http://localhost:5000/list-models` | List available models |
| `pkill -f "main.py"` | Kill ComfyUI |
| `python start_with_ngrok.py` | Restart everything |

---

**Made with ❤️ to help you debug AI image generation**
