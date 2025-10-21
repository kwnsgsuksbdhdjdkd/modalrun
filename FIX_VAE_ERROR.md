# 🔧 Fix: VAE File Corrupted Error

## ❌ The Error

```
ComfyUI error in VAELoader: Error while deserializing header: header too large
```

This means your `ae.safetensors` file is **corrupted** or **incompletely downloaded**.

---

## ✅ Solution: Re-download the VAE File

### Step 1: Remove the Corrupted File

```bash
rm /root/ComfyUI/models/vae/ae.safetensors
```

### Step 2: Download Fresh Copy

**Option A: From Black Forest Labs (Official)**
```bash
cd /root/ComfyUI/models/vae/
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors
```

**Option B: From Stability AI**
```bash
cd /root/ComfyUI/models/vae/
wget https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors -O ae.safetensors
```

### Step 3: Verify the File

```bash
ls -lh /root/ComfyUI/models/vae/ae.safetensors
```

Should show approximately **320-335 MB**:
```
-rw-r--r-- 1 root root 335M Oct 21 12:34 ae.safetensors
```

### Step 4: Restart Your Server

```bash
cd /root/comfyui-api
python start_with_ngrok.py
```

---

## 🔍 Check Other Model Files

If you're still having issues, verify ALL your model files:

### Check UNET/Model Files:
```bash
ls -lh /root/ComfyUI/models/unet/
ls -lh /root/ComfyUI/models/checkpoints/
```

### Check CLIP Files:
```bash
ls -lh /root/ComfyUI/models/clip/
```

Expected files:
- `clip_l.safetensors` (~235 MB)
- `t5xxl_fp16.safetensors` (~9.3 GB)

### Check VAE Files:
```bash
ls -lh /root/ComfyUI/models/vae/
```

Expected:
- `ae.safetensors` (~335 MB)

---

## 🎯 Quick Fix Script

Save this as `fix_vae.sh` and run it:

```bash
#!/bin/bash

echo "🔧 Fixing VAE file..."

# Remove corrupted file
echo "1️⃣ Removing corrupted file..."
rm -f /root/ComfyUI/models/vae/ae.safetensors

# Download fresh copy
echo "2️⃣ Downloading fresh VAE file..."
cd /root/ComfyUI/models/vae/
wget -q --show-progress https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors

# Verify
echo "3️⃣ Verifying download..."
if [ -f "ae.safetensors" ]; then
    SIZE=$(stat -c%s "ae.safetensors")
    if [ $SIZE -gt 300000000 ]; then
        echo "✅ VAE file downloaded successfully!"
        echo "   Size: $(($SIZE / 1024 / 1024)) MB"
    else
        echo "❌ File too small! Download may have failed."
        exit 1
    fi
else
    echo "❌ File not found! Download failed."
    exit 1
fi

echo "✅ Fix complete! Restart your server."
```

Run it:
```bash
chmod +x fix_vae.sh
./fix_vae.sh
```

---

## 🚨 If Still Not Working

### Check Disk Space
```bash
df -h /root
```

Make sure you have at least **10 GB free**.

### Check Network Connection
```bash
ping -c 3 huggingface.co
```

### Manual Download with Retry
```bash
cd /root/ComfyUI/models/vae/
wget --continue --tries=5 https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors
```

---

## 💡 Alternative: Use Different Workflow

If you can't fix the VAE, use a different workflow that doesn't require it.

Edit `notebook_comfyui_api.py` and change the workflow to use **Stable Diffusion** instead of FLUX.

---

## ✅ After Fix

You should see:
```
✅ Queued prompt abc-123... for user 90a5df03...
⏳ Waiting for generation...
✅ Image generated in 45.2s for user 90a5df03...
📤 Sent image to user 90a5df03... via SocketIO
```

**No more "header too large" errors!**

---

Generated: 2025-10-21
Issue: Corrupted VAE file `ae.safetensors`
