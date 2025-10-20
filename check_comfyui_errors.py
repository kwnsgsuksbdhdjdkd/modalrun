#!/usr/bin/env python3
"""
ComfyUI Error Checker - Run this to diagnose why image generation fails
Usage: python check_comfyui_errors.py [prompt_id]
"""

import sys
import requests
import json
from pathlib import Path

COMFYUI_URL = "http://localhost:8188"

def check_comfyui_running():
    """Check if ComfyUI is running"""
    print("=" * 60)
    print("1. CHECKING COMFYUI STATUS")
    print("=" * 60)
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("✅ ComfyUI is running!")
            print(f"   System Stats: {json.dumps(stats, indent=2)}")
            return True
        else:
            print(f"❌ ComfyUI returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to ComfyUI on port 8188")
        print("   Is ComfyUI running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_models():
    """Check available models"""
    print("\n" + "=" * 60)
    print("2. CHECKING AVAILABLE MODELS")
    print("=" * 60)
    
    models_dir = Path("/root/ComfyUI/models/checkpoints")
    if not models_dir.exists():
        print(f"❌ Models directory not found: {models_dir}")
        return []
    
    models = list(models_dir.glob("*.safetensors"))
    if models:
        print(f"✅ Found {len(models)} model(s):")
        for model in models:
            size_mb = model.stat().st_size / (1024 * 1024)
            print(f"   - {model.name} ({size_mb:.0f} MB)")
        return [m.name for m in models]
    else:
        print("❌ No models found in checkpoints directory!")
        print(f"   Download a model to: {models_dir}")
        return []

def check_queue():
    """Check ComfyUI queue status"""
    print("\n" + "=" * 60)
    print("3. CHECKING QUEUE STATUS")
    print("=" * 60)
    try:
        response = requests.get(f"{COMFYUI_URL}/queue", timeout=5)
        if response.status_code == 200:
            queue_data = response.json()
            running = queue_data.get("queue_running", [])
            pending = queue_data.get("queue_pending", [])
            
            print(f"   Running: {len(running)} tasks")
            print(f"   Pending: {len(pending)} tasks")
            
            if running:
                print("\n   Currently running:")
                for item in running:
                    print(f"   - Prompt ID: {item[1] if len(item) > 1 else 'unknown'}")
            
            return True
        else:
            print(f"❌ Queue check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking queue: {e}")
        return False

def check_prompt_history(prompt_id=None):
    """Check prompt execution history"""
    print("\n" + "=" * 60)
    print("4. CHECKING PROMPT HISTORY")
    print("=" * 60)
    
    try:
        if prompt_id:
            url = f"{COMFYUI_URL}/history/{prompt_id}"
            print(f"   Checking specific prompt: {prompt_id}")
        else:
            url = f"{COMFYUI_URL}/history"
            print("   Checking all recent history...")
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            history = response.json()
            
            if not history:
                print("⚠️  No history found - ComfyUI may have just started")
                return None
            
            if prompt_id and prompt_id in history:
                print(f"\n✅ Found prompt {prompt_id}:")
                prompt_data = history[prompt_id]
                print(f"   Status: {json.dumps(prompt_data.get('status', {}), indent=4)}")
                
                # Check for errors
                if 'status' in prompt_data:
                    status = prompt_data['status']
                    if 'status_str' in status and status['status_str'] == 'error':
                        print("\n❌ EXECUTION ERROR FOUND:")
                        print(json.dumps(status, indent=4))
                    if 'messages' in status:
                        print("\n📝 Messages:")
                        for msg in status['messages']:
                            print(f"   - {msg}")
                
                # Check outputs
                outputs = prompt_data.get('outputs', {})
                if outputs:
                    print(f"\n✅ Outputs found:")
                    for node_id, output in outputs.items():
                        print(f"   Node {node_id}: {output}")
                else:
                    print("\n❌ No outputs found!")
                
                return prompt_data
            elif prompt_id:
                print(f"❌ Prompt {prompt_id} not found in history")
                print("\n   Available prompts:")
                for pid in list(history.keys())[:5]:
                    print(f"   - {pid}")
                return None
            else:
                print(f"✅ Found {len(history)} prompts in history")
                print("\n   Recent prompts:")
                for pid in list(history.keys())[:5]:
                    status = history[pid].get('status', {})
                    status_str = status.get('status_str', 'unknown')
                    print(f"   - {pid}: {status_str}")
                return history
        else:
            print(f"❌ History check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error checking history: {e}")
        return None

def test_simple_workflow():
    """Test with a minimal workflow"""
    print("\n" + "=" * 60)
    print("5. TESTING SIMPLE WORKFLOW")
    print("=" * 60)
    
    models = check_models()
    if not models:
        print("❌ Cannot test - no models available")
        return False
    
    # Use first available model
    model_name = models[0]
    print(f"   Using model: {model_name}")
    
    # Create minimal test workflow
    test_workflow = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": model_name
            }
        }
    }
    
    print("   Sending test workflow (just load model)...")
    try:
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": test_workflow, "client_id": "test"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test workflow queued: {result.get('prompt_id')}")
            
            if result.get('node_errors'):
                print("\n❌ NODE ERRORS FOUND:")
                print(json.dumps(result['node_errors'], indent=4))
                return False
            
            return True
        else:
            print(f"❌ Failed to queue: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║         ComfyUI Error Diagnostic Tool                 ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    prompt_id = sys.argv[1] if len(sys.argv) > 1 else None
    if prompt_id:
        print(f"Checking prompt: {prompt_id}\n")
    
    # Run all checks
    running = check_comfyui_running()
    if not running:
        print("\n" + "=" * 60)
        print("DIAGNOSIS: ComfyUI is not running!")
        print("=" * 60)
        print("\n💡 Fix: Start ComfyUI with:")
        print("   cd /root/ComfyUI")
        print("   python main.py --listen 0.0.0.0 --port 8188")
        return
    
    models = check_models()
    check_queue()
    
    if prompt_id:
        history = check_prompt_history(prompt_id)
    else:
        history = check_prompt_history()
    
    test_simple_workflow()
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    if not models:
        print("\n❌ CRITICAL: No models found!")
        print("   Download a model:")
        print("   cd /root/ComfyUI/models/checkpoints/")
        print("   wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors")
    elif running:
        print("\n✅ ComfyUI is running")
        print(f"✅ {len(models)} model(s) available")
        
        if prompt_id and history:
            print(f"\n📊 Check the output above for prompt {prompt_id} details")
        
        print("\n💡 If generation is failing, check:")
        print("   1. Model name in workflow matches available models")
        print("   2. ComfyUI console output for errors")
        print("   3. GPU memory availability")

if __name__ == "__main__":
    main()
