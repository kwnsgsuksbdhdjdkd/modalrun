#!/bin/bash

# ComfyUI API Setup Script for Modal Notebooks
# Run this script in your Modal notebook to set up everything automatically

echo "╔════════════════════════════════════════════════════════╗"
echo "║  🎨 ComfyUI API Setup for Modal Notebooks             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check if we're in the right place
echo "📍 Step 1: Checking environment..."
if [ ! -d "/root/ComfyUI" ]; then
    echo "❌ Error: /root/ComfyUI not found. Are you in a Modal notebook?"
    exit 1
fi
echo "✅ ComfyUI directory found"

# Step 2: Install dependencies
echo ""
echo "📦 Step 2: Installing Python dependencies..."
pip install flask requests pyngrok -q
echo "✅ Dependencies installed"

# Step 3: Check for models
echo ""
echo "🎨 Step 3: Checking for models..."
MODELS_DIR="/root/ComfyUI/models/checkpoints"
MODEL_COUNT=$(ls -1 $MODELS_DIR/*.safetensors 2>/dev/null | wc -l)

if [ $MODEL_COUNT -eq 0 ]; then
    echo "⚠️  No models found. Would you like to download FLUX.1-schnell? (23GB, ~5 min)"
    echo "   This is required to generate images."
    read -p "   Download now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "⬇️  Downloading FLUX.1-schnell model..."
        cd $MODELS_DIR
        wget -q --show-progress https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors
        echo "✅ Model downloaded"
    else
        echo "⚠️  Skipping model download. You'll need to add models manually."
    fi
else
    echo "✅ Found $MODEL_COUNT model(s):"
    ls -1 $MODELS_DIR/*.safetensors 2>/dev/null | xargs -n 1 basename
fi

# Step 4: Create project directory
echo ""
echo "📁 Step 4: Setting up project directory..."
PROJECT_DIR="/root/comfyui-api"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR
echo "✅ Project directory: $PROJECT_DIR"

# Step 5: Check if files exist
echo ""
echo "📝 Step 5: Checking project files..."
if [ ! -f "notebook_comfyui_api.py" ]; then
    echo "⚠️  notebook_comfyui_api.py not found in $PROJECT_DIR"
    echo "   Please upload the project files to this directory."
    echo ""
    echo "   Files needed:"
    echo "   - notebook_comfyui_api.py"
    echo "   - config.json (optional)"
    echo ""
    exit 1
fi
echo "✅ Project files found"

# Step 6: Test configuration
echo ""
echo "⚙️  Step 6: Configuration..."
if [ -f "config.json" ]; then
    echo "✅ config.json found"
else
    echo "⚠️  config.json not found (Discord notifications disabled)"
fi

# Step 7: Ready to start
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 To start the API server, run:"
echo ""
echo "   cd $PROJECT_DIR"
echo "   python notebook_comfyui_api.py"
echo ""
echo "🌍 For public access via ngrok, run:"
echo ""
echo "   python start_with_ngrok.py"
echo ""
echo "📖 See NOTEBOOK_SETUP.md for detailed instructions"
echo ""

