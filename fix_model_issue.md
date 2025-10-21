# 🔧 Fix: CLIP Text Encoder Missing from Model

## 🐛 **Your Error**

```
ERROR: clip input is invalid: None

If the clip is from a checkpoint loader node your checkpoint 
does not contain a valid clip or text encoder model.
```

## 🎯 **What This Means**

Your `flux1-krea-dev.safetensors` model file is **missing the CLIP text encoder** or is **incomplete/corrupted**.

FLUX models need 3 components:
1. ✅ **Model** (diffusion model) - Working
2. ❌ **CLIP** (text encoder) - Missing!
3. ⚠️ **VAE** (image decoder) - Unknown

---

## ✅ **Solution 1: Download Proper FLUX Model** (Recommended)

Replace your model with the official FLUX.1-schnell:

### **In Your Modal Notebook:**

```bash
# Go to models directory
cd /root/ComfyUI/models/checkpoints/

# Backup old model (optional)
mv flux1-krea-dev.safetensors flux1-krea-dev.safetensors.backup

# Download official FLUX.1-schnell (23GB, ~5-10 minutes)
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors

# Verify download (should be ~23GB)
ls -lh flux1-schnell.safetensors
```

### **Update the Code:**

Then change `/root/comfyui-api/notebook_comfyui_api.py` line 57:

```python
# Change FROM:
"ckpt_name": "flux1-krea-dev.safetensors"

# Change TO:
"ckpt_name": "flux1-schnell.safetensors"
```

### **Restart:**

```bash
cd /root/comfyui-api
pkill -f "main.py"
python start_with_ngrok.py
```

---

## ✅ **Solution 2: Check if Model is Complete**

Your model might be corrupted or incomplete:

```bash
cd /root/ComfyUI/models/checkpoints/

# Check file size
ls -lh flux1-krea-dev.safetensors

# Should be ~20-25GB for FLUX models
# If it's much smaller, it's incomplete!
```

**If file is incomplete:**
- Re-download the model
- Make sure download completed fully
- Check disk space: `df -h`

---

## ✅ **Solution 3: Use Separate CLIP Model** (Advanced)

If `flux1-krea-dev` is a special model without CLIP, you need to load CLIP separately.

### **Download CLIP Model:**

```bash
cd /root/ComfyUI/models/clip/
wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors
wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors
```

### **Use Different Workflow:**

You'll need a workflow that loads CLIP separately - this is more complex.

---

## ✅ **Solution 4: Use Different Model** (Fastest)

If you have other models available:

### **Check Available Models:**

```bash
ls -lh /root/ComfyUI/models/checkpoints/
```

### **Use the Diagnostic Tool:**

```bash
cd /root/comfyui-api
python check_comfyui_errors.py
```

This will list all available models and their sizes.

---

## 🚀 **Quick Fix (Recommended)**

Run this script in your Modal notebook:

```bash
#!/bin/bash

echo "🔧 Fixing FLUX Model Issue..."

# Kill existing processes
pkill -9 -f "main.py"
sleep 2

# Go to models directory
cd /root/ComfyUI/models/checkpoints/

# Check current model
echo "📊 Current model:"
ls -lh flux1-krea-dev.safetensors 2>/dev/null || echo "   Model not found"

# Download proper FLUX model
echo "📥 Downloading FLUX.1-schnell (23GB, ~10 min)..."
echo "   (You can cancel if you already have it)"
wget -c https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors

# Check download
if [ -f "flux1-schnell.safetensors" ]; then
    size=$(stat -f%z flux1-schnell.safetensors 2>/dev/null || stat -c%s flux1-schnell.safetensors)
    echo "✅ flux1-schnell.safetensors: $size bytes"
    
    # Update API code
    echo "📝 Updating API code..."
    cd /root/comfyui-api
    sed -i 's/flux1-krea-dev.safetensors/flux1-schnell.safetensors/g' notebook_comfyui_api.py
    
    echo "✅ Fixed! Now restart:"
    echo "   cd /root/comfyui-api && python start_with_ngrok.py"
else
    echo "❌ Download failed. Check internet connection."
fi
```

**Save as:** `fix_model.sh`  
**Run:** `bash fix_model.sh`

---

## 🔍 **Understanding the Error**

### **What Happened:**

1. ✅ ComfyUI started successfully
2. ✅ API queued your request
3. ✅ Model file loaded (`flux1-krea-dev.safetensors`)
4. ❌ **CLIP text encoder is missing from model**
5. ❌ Can't encode your text prompt
6. ❌ Generation fails

### **Why This Happens:**

- **Incomplete download**: Model file is corrupted/incomplete
- **Custom model**: `flux1-krea-dev` is a modified version without CLIP
- **Wrong model type**: Not a full FLUX checkpoint
- **Corrupted file**: Download was interrupted

---

## 📋 **Quick Decision Guide**

| Situation | Solution |
|-----------|----------|
| **Want it to just work** | Download `flux1-schnell.safetensors` (Solution 1) |
| **Model is too small (<20GB)** | Re-download complete model |
| **Have other models** | Switch to different model |
| **Advanced user** | Load CLIP separately (Solution 3) |

---

## ✅ **Verification**

After fixing, test:

```bash
curl -X POST https://YOUR-URL/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a cute cat wearing sunglasses"}' \
  --output cat.png
```

**Expected:** Image generation completes in 20-60 seconds

---

## 🆘 **Still Not Working?**

### **Check Model File:**

```bash
cd /root/ComfyUI/models/checkpoints/
ls -lh *.safetensors

# FLUX models should be ~20-25GB
# If your file is much smaller, it's incomplete!
```

### **Try Official Model:**

The safest bet is always the official FLUX.1-schnell:

```bash
cd /root/ComfyUI/models/checkpoints/
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
```

Then update code to use `flux1-schnell.safetensors`

---

## 📝 **Summary**

**Problem:** `flux1-krea-dev.safetensors` doesn't have CLIP text encoder  
**Solution:** Download proper `flux1-schnell.safetensors` model  
**Time:** 10 minutes to download + 2 minutes to configure  
**Result:** Working image generation! 🎉

---

**Try Solution 1 (download flux1-schnell) - it's the most reliable fix!** 🚀
