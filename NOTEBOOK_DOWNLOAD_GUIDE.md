# 🎨 Download FLUX.1-Krea-dev Model in Modal Notebook

## 📋 Quick Start (For Jupyter Notebooks)

Copy and paste these commands into separate cells in your Modal Jupyter notebook:

### Cell 1: Download the Python script
```python
!wget https://raw.githubusercontent.com/kwnsgsuksbdhdjdkd/modalrun/main/download_flux_krea_model.py
```

### Cell 2: Edit the credentials in the file
```python
# Open the file and replace YOUR_HF_USERNAME_HERE and YOUR_HF_TOKEN_HERE
# with your actual HuggingFace credentials
!nano download_flux_krea_model.py

# Or edit it programmatically:
import re

with open('download_flux_krea_model.py', 'r') as f:
    content = f.read()

# Replace with your credentials
content = content.replace('YOUR_HF_USERNAME_HERE', 'your_actual_username')
content = content.replace('YOUR_HF_TOKEN_HERE', 'your_actual_token')

with open('download_flux_krea_model.py', 'w') as f:
    f.write(content)

print("✅ Credentials updated!")
```

### Cell 3: Run the downloader
```python
!python download_flux_krea_model.py
```

---

## ⚡ Alternative: Direct Shell Commands

If you prefer shell commands, run this in a notebook cell:

```python
# Install git-lfs
!apt-get update && apt-get install -y git-lfs
!git lfs install

# Configure credentials (REPLACE WITH YOUR OWN!)
!git config --global credential.helper store
!echo "https://YOUR_USERNAME:YOUR_TOKEN@huggingface.co" > ~/.git-credentials
!chmod 600 ~/.git-credentials

# Create directories
!mkdir -p /root/ComfyUI/models/checkpoints
!mkdir -p /root/ComfyUI/models/clip

# Download FLUX model
!cd /tmp && git clone https://huggingface.co/black-forest-labs/FLUX.1-Krea-dev
!mv /tmp/FLUX.1-Krea-dev/*.safetensors /root/ComfyUI/models/checkpoints/

# Download text encoders
!cd /root/ComfyUI/models/clip && \
 wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors && \
 wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors

# Verify
!ls -lh /root/ComfyUI/models/checkpoints/*.safetensors
!ls -lh /root/ComfyUI/models/clip/*.safetensors

# Clean up
!rm -rf /tmp/FLUX.1-Krea-dev
!rm ~/.git-credentials
```

---

## ⏱️ Timing & Requirements

- **Total Download:** ~35GB
- **Estimated Time:** 15-30 minutes
- **Disk Space:** Need 40GB+ free

---

## 🚀 After Download

Once complete, restart ComfyUI:

```python
!cd /root/comfyui-api && pkill -f 'main.py'
!cd /root/comfyui-api && python start_with_ngrok.py
```

---

## ✅ Verification

Check that all files downloaded correctly:

```python
!ls -lh /root/ComfyUI/models/checkpoints/*.safetensors
!ls -lh /root/ComfyUI/models/clip/*.safetensors
```

You should see:
- 1 model file in checkpoints/ (20-25GB)
- 2 encoder files in clip/ (4GB + 9.5GB)
