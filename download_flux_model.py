#!/usr/bin/env python3
"""
FLUX.1-Krea-dev Model Downloader for Modal Notebooks
Downloads FLUX model and all required components (CLIP, T5 encoders)

USAGE IN JUPYTER NOTEBOOK:
    1. Download this script
    2. Edit lines 18-19 with your HuggingFace credentials
    3. Run: !python download_flux_model.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# ⚠️ REPLACE THESE WITH YOUR HUGGINGFACE CREDENTIALS!
HF_USERNAME = "ebinesar00005"
HF_TOKEN = "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"

# Directories
COMFYUI_DIR = "/root/ComfyUI"
MODELS_DIR = f"{COMFYUI_DIR}/models"
CHECKPOINTS_DIR = f"{MODELS_DIR}/checkpoints"
CLIP_DIR = f"{MODELS_DIR}/clip"
VAE_DIR = f"{MODELS_DIR}/vae"

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def run_command(cmd, description, show_output=True):
    """Run a shell command with error handling"""
    print(f"\n🔄 {description}...")
    try:
        if show_output:
            result = subprocess.run(cmd, shell=True, check=True, text=True)
        else:
            result = subprocess.run(
                cmd, shell=True, check=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        print(f"✅ {description} - Done!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def check_disk_space():
    """Check available disk space"""
    print_header("Checking Disk Space")
    result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    print(result.stdout)
    
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        parts = lines[1].split()
        available = parts[3]
        print(f"\n📊 Available space: {available}")
        print("💡 You need ~35GB free (23GB model + 12GB encoders)")

def setup_git_credentials():
    """Configure git with HuggingFace credentials"""
    print_header("Setting Up Git Credentials")
    
    if HF_USERNAME == "YOUR_HF_USERNAME_HERE" or HF_TOKEN == "YOUR_HF_TOKEN_HERE":
        print("❌ ERROR: Please edit lines 18-19 with your HuggingFace credentials!")
        print("   Get your token from: https://huggingface.co/settings/tokens")
        sys.exit(1)
    
    run_command(
        "git config --global credential.helper store",
        "Configuring git credential helper",
        show_output=False
    )
    
    credentials_path = Path.home() / ".git-credentials"
    credentials_content = f"https://{HF_USERNAME}:{HF_TOKEN}@huggingface.co\n"
    
    with open(credentials_path, 'w') as f:
        f.write(credentials_content)
    
    os.chmod(credentials_path, 0o600)
    print("✅ Git credentials configured")

def install_git_lfs():
    """Install git-lfs if not present"""
    print_header("Checking Git LFS")
    
    result = subprocess.run(["which", "git-lfs"], capture_output=True)
    if result.returncode != 0:
        print("📦 Installing git-lfs...")
        run_command(
            "apt-get update && apt-get install -y git-lfs",
            "Installing git-lfs"
        )
    else:
        print("✅ git-lfs already installed")
    
    run_command("git lfs install", "Initializing git-lfs", show_output=False)

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    dirs = [CHECKPOINTS_DIR, CLIP_DIR, VAE_DIR]
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")

def download_flux_krea_model():
    """Download FLUX.1-Krea-dev model from HuggingFace"""
    print_header("Downloading FLUX.1-Krea-dev Model")
    
    model_repo = "https://huggingface.co/black-forest-labs/FLUX.1-Krea-dev"
    temp_dir = "/tmp/flux-krea-download"
    
    if os.path.exists(temp_dir):
        print("🧹 Cleaning up old download directory...")
        subprocess.run(["rm", "-rf", temp_dir])
    
    print(f"\n📥 Cloning repository from: {model_repo}")
    print("⏰ This will take 10-20 minutes (23GB+ download)")
    print("💡 Please be patient...\n")
    
    cmd = f"GIT_LFS_SKIP_SMUDGE=0 git clone {model_repo} {temp_dir}"
    success = run_command(cmd, "Downloading FLUX.1-Krea-dev")
    
    if not success:
        print("\n❌ Download failed!")
        return False
    
    print("\n📦 Moving files to correct directories...")
    
    temp_path = Path(temp_dir)
    
    for file in temp_path.glob("*.safetensors"):
        if "clip" in file.name.lower():
            dest = Path(CLIP_DIR) / file.name
        elif "vae" in file.name.lower():
            dest = Path(VAE_DIR) / file.name
        else:
            dest = Path(CHECKPOINTS_DIR) / file.name
        
        print(f"📁 Moving {file.name} -> {dest.parent.name}/")
        subprocess.run(["mv", str(file), str(dest)])
    
    print("\n🧹 Cleaning up temporary files...")
    subprocess.run(["rm", "-rf", temp_dir])
    
    return True

def download_text_encoders():
    """Download CLIP and T5 text encoders if not in model"""
    print_header("Downloading Text Encoders")
    
    print("📥 Downloading CLIP L encoder...")
    clip_url = "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
    clip_path = f"{CLIP_DIR}/clip_l.safetensors"
    
    if not os.path.exists(clip_path):
        cmd = f'wget --header="Authorization: Bearer {HF_TOKEN}" -O {clip_path} {clip_url}'
        run_command(cmd, "Downloading CLIP encoder (~4GB)")
    else:
        print("✅ CLIP encoder already exists")
    
    print("\n📥 Downloading T5-XXL encoder...")
    t5_url = "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors"
    t5_path = f"{CLIP_DIR}/t5xxl_fp16.safetensors"
    
    if not os.path.exists(t5_path):
        cmd = f'wget --header="Authorization: Bearer {HF_TOKEN}" -O {t5_path} {t5_url}' 
        run_command(cmd, "Downloading T5 encoder (~9.5GB)")
    else:
        print("✅ T5 encoder already exists")

def verify_downloads():
    """Verify all files were downloaded correctly"""
    print_header("Verifying Downloads")
    
    files_to_check = {
        "Model checkpoint": CHECKPOINTS_DIR,
        "CLIP encoders": CLIP_DIR,
    }
    
    all_good = True
    for name, directory in files_to_check.items():
        files = list(Path(directory).glob("*.safetensors"))
        if files:
            print(f"\n✅ {name}:")
            for file in files:
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"   📄 {file.name} ({size_mb:.0f} MB)")
        else:
            print(f"\n❌ {name}: No files found in {directory}")
            all_good = False
    
    return all_good

def print_summary():
    """Print summary and next steps"""
    print_header("🎉 Download Complete!")
    
    print("\n✅ All files downloaded successfully!")
    print("\n📁 File Locations:")
    print(f"   Models: {CHECKPOINTS_DIR}")
    print(f"   CLIP/T5: {CLIP_DIR}")
    
    print("\n🚀 Next Steps:")
    print("   1. Update your API code to use the new model")
    print("   2. Restart ComfyUI API:")
    print("      cd /root/comfyui-api")
    print("      pkill -f 'main.py'")
    print("      python start_with_ngrok.py")
    
    print("\n" + "=" * 70)

def main():
    """Main download process"""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🎨 FLUX.1-Krea-dev Model Downloader".center(68) + "║")
    print("║" + "  for Modal Notebooks".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    print("\n⚠️  IMPORTANT:")
    print("   - This will download ~35GB of files")
    print("   - Estimated time: 15-30 minutes")
    print("   - Make sure you have stable internet connection")
    print("\n   Press Ctrl+C to cancel within 5 seconds...")
    
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
    
    start_time = time.time()
    
    check_disk_space()
    setup_git_credentials()
    install_git_lfs()
    create_directories()
    
    if not download_flux_krea_model():
        print("\n❌ Failed to download model!")
        sys.exit(1)
    
    download_text_encoders()
    
    if not verify_downloads():
        print("\n⚠️  Some files may be missing. Check the output above.")
    
    elapsed = time.time() - start_time
    minutes = int(elapsed / 60)
    seconds = int(elapsed % 60)
    
    print(f"\n⏱️  Total time: {minutes}m {seconds}s")
    
    # Clean up credentials
    credentials_path = Path.home() / ".git-credentials"
    if credentials_path.exists():
        credentials_path.unlink()
        print("🔒 Cleaned up credentials file")
    
    print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
