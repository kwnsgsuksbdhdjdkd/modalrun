# Models Guide for ComfyUI on Modal

This guide explains how to upload and manage models for your ComfyUI Modal deployment.

## Model Categories

ComfyUI organizes models into categories:

- **checkpoints**: Main diffusion models (FLUX, SD, SDXL, etc.)
- **vae**: Variational Autoencoders
- **clip**: CLIP text encoders
- **unet**: U-Net models (for FLUX/SD3)
- **loras**: LoRA fine-tuning models
- **controlnet**: ControlNet models
- **upscale**: Upscaling models

## Recommended Models

### FLUX.1-schnell (Recommended)
Fast, high-quality image generation (4 steps)

```bash
modal run modal_comfyui_app.py::upload_model \
  --model-url "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors" \
  --model-category "checkpoints" \
  --model-name "flux1-schnell.safetensors"
```

### FLUX.1-dev
Higher quality, slower (50 steps)

```bash
modal run modal_comfyui_app.py::upload_model \
  --model-url "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors" \
  --model-category "checkpoints" \
  --model-name "flux1-dev.safetensors"
```

### Stable Diffusion XL
Popular alternative model

```bash
modal run modal_comfyui_app.py::upload_model \
  --model-url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --model-category "checkpoints" \
  --model-name "sd_xl_base_1.0.safetensors"
```

## Upload from Local Files

If you have models on your local machine:

### Method 1: Using Modal CLI

```bash
# Upload to Modal volume
modal volume put comfyui-models /path/to/local/model.safetensors /models/checkpoints/model.safetensors
```

### Method 2: Upload via Python

```python
import modal

# Get the volume
volume = modal.Volume.from_name("comfyui-models")

# Upload file
with open("/path/to/local/model.safetensors", "rb") as f:
    volume.put("/models/checkpoints/model.safetensors", f)
```

## Managing Models

### List Uploaded Models

```bash
modal volume ls comfyui-models /models/
```

### Check Specific Category

```bash
modal volume ls comfyui-models /models/checkpoints/
```

### Remove a Model

```bash
modal volume rm comfyui-models /models/checkpoints/old_model.safetensors
```

### Check Model via API

```bash
curl https://YOUR-APP--list-models.modal.run
```

## Model Sources

### HuggingFace
- [FLUX Models](https://huggingface.co/black-forest-labs)
- [Stable Diffusion](https://huggingface.co/stabilityai)
- [Community Models](https://huggingface.co/models?pipeline_tag=text-to-image)

### CivitAI
Popular community models (requires manual download)

1. Download model from [CivitAI](https://civitai.com)
2. Upload using Modal CLI or volume API

## Model Configuration

After uploading, update your workflow JSON:

```json
{
  "4": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "flux1-schnell.safetensors"
    }
  }
}
```

The `ckpt_name` must match the exact filename in `/models/checkpoints/`.

## LoRAs and Custom Models

### Upload LoRA

```bash
modal run modal_comfyui_app.py::upload_model \
  --model-url "https://example.com/my-lora.safetensors" \
  --model-category "loras" \
  --model-name "my-lora.safetensors"
```

### Use LoRA in Workflow

Add a LoRA loader node:

```json
{
  "10": {
    "class_type": "LoraLoader",
    "inputs": {
      "lora_name": "my-lora.safetensors",
      "strength_model": 1.0,
      "strength_clip": 1.0,
      "model": ["4", 0],
      "clip": ["4", 1]
    }
  }
}
```

## Storage & Costs

Modal volumes are billed at **$0.10/GB/month**.

Typical model sizes:
- FLUX.1-schnell: ~23GB
- FLUX.1-dev: ~23GB
- SDXL: ~7GB
- LoRAs: 10-200MB each

**Tip**: Only upload models you actively use to minimize costs.

## Troubleshooting

### "Model not found" error

1. Check model exists:
   ```bash
   modal volume ls comfyui-models /models/checkpoints/
   ```

2. Verify exact filename in workflow matches uploaded file

3. Check model category is correct

### Upload timeouts

For large models (>20GB):
- Increase timeout in upload function
- Use direct volume upload instead
- Upload from a cloud VM for faster transfer

### Model compatibility

- FLUX models require recent ComfyUI version
- Some models need specific VAE files
- Check model documentation for requirements

## Best Practices

1. **Start Small**: Upload one model, test, then add more
2. **Use Fast Models**: FLUX.1-schnell for development
3. **Clean Up**: Remove unused models to save costs
4. **Version Control**: Include model versions in filenames
5. **Documentation**: Keep track of which models work with which workflows

## Example: Complete Setup

```bash
# 1. Upload base model
modal run modal_comfyui_app.py::upload_model \
  --model-url "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors" \
  --model-category "checkpoints" \
  --model-name "flux1-schnell.safetensors"

# 2. Verify upload
modal volume ls comfyui-models /models/checkpoints/

# 3. Test via API
curl https://YOUR-APP--list-models.modal.run

# 4. Generate image
curl -X POST https://YOUR-APP--generate.modal.run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test image"}' \
  --output test.png
```

---

Need help? Check the [main README](README.md) or [Quick Start Guide](QUICKSTART.md).


