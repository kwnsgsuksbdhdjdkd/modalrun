#!/usr/bin/env python3
"""
Fix Model File Locations for ComfyUI
Moves FLUX model files to correct directories
"""

import os
import shutil
from pathlib import Path

# Directories
COMFYUI_DIR = "/root/ComfyUI"
CHECKPOINTS_DIR = f"{COMFYUI_DIR}/models/checkpoints"
UNET_DIR = f"{COMFYUI_DIR}/models/unet"
VAE_DIR = f"{COMFYUI_DIR}/models/vae"
CLIP_DIR = f"{COMFYUI_DIR}/models/clip"

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    dirs = [UNET_DIR, VAE_DIR, CLIP_DIR]
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")

def move_files():
    """Move files to correct locations"""
    print_header("Moving Files to Correct Locations")
    
    checkpoints_path = Path(CHECKPOINTS_DIR)
    
    # Move FLUX UNET model
    flux_file = checkpoints_path / "flux1-krea-dev.safetensors"
    if flux_file.exists():
        dest = Path(UNET_DIR) / "flux1-krea-dev.safetensors"
        if not dest.exists():
            print(f"📁 Moving flux1-krea-dev.safetensors: checkpoints/ -> unet/")
            shutil.move(str(flux_file), str(dest))
            print(f"   ✅ Moved to {dest}")
        else:
            print(f"   ℹ️  flux1-krea-dev.safetensors already in unet/")
    else:
        print(f"   ⚠️  flux1-krea-dev.safetensors not found in checkpoints/")
    
    # Move VAE file
    vae_file = checkpoints_path / "ae.safetensors"
    if vae_file.exists():
        dest = Path(VAE_DIR) / "ae.safetensors"
        if not dest.exists():
            print(f"📁 Moving ae.safetensors: checkpoints/ -> vae/")
            shutil.move(str(vae_file), str(dest))
            print(f"   ✅ Moved to {dest}")
        else:
            print(f"   ℹ️  ae.safetensors already in vae/")
    else:
        print(f"   ⚠️  ae.safetensors not found in checkpoints/")

def verify_locations():
    """Verify all files are in correct locations"""
    print_header("Verifying File Locations")
    
    checks = {
        "UNET Model": Path(UNET_DIR) / "flux1-krea-dev.safetensors",
        "VAE Model": Path(VAE_DIR) / "ae.safetensors",
        "CLIP Encoder": Path(CLIP_DIR) / "clip_l.safetensors",
        "T5 Encoder": Path(CLIP_DIR) / "t5xxl_fp16.safetensors",
    }
    
    all_good = True
    for name, filepath in checks.items():
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"✅ {name}: {filepath.name} ({size_mb:.0f} MB)")
        else:
            print(f"❌ {name}: NOT FOUND at {filepath}")
            all_good = False
    
    return all_good

def main():
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🔧 Fix FLUX Model File Locations".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    create_directories()
    move_files()
    
    if verify_locations():
        print_header("🎉 All Files in Correct Locations!")
        print("\n✅ Ready to use with ComfyUI!")
        print("\n🚀 Next Steps:")
        print("   1. Restart ComfyUI API:")
        print("      cd /root/comfyui-api")
        print("      pkill -f 'main.py'")
        print("      python start_with_ngrok.py")
        print("\n   2. Test image generation!")
    else:
        print_header("⚠️  Some Files Are Missing")
        print("\nPlease check the output above and ensure all files were downloaded.")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
