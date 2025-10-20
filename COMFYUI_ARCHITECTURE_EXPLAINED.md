# 🏗️ ComfyUI Architecture - Complete Technical Explanation

## 📚 Table of Contents

1. [Overview](#overview)
2. [Architecture Components](#architecture-components)
3. [How Image Generation Works](#how-image-generation-works)
4. [API System](#api-system)
5. [Workflow Structure](#workflow-structure)
6. [Node System](#node-system)
7. [Execution Flow](#execution-flow)
8. [How Our Implementation Works](#how-our-implementation-works)

---

## 🎯 Overview

**ComfyUI** is a node-based workflow engine for AI image generation. It uses a graph/flowchart interface where:
- **Nodes** = Processing units (load model, encode text, generate image, etc.)
- **Edges** = Data connections between nodes
- **Workflow** = JSON definition of nodes and their connections
- **Execution** = Processing the workflow graph to generate images

---

## 🏗️ Architecture Components

### **1. Main Entry Point (`main.py`)**

```python
# main.py - Starts ComfyUI server

# Key functions:
start_comfyui(asyncio_loop=None)
  └─> Creates server instance
  └─> Initializes nodes and custom nodes
  └─> Starts prompt queue worker thread
  └─> Starts HTTP server (default port 8188)
```

**What it does:**
- Sets up GPU configuration
- Loads custom nodes
- Initializes model paths
- Starts async event loop
- Creates HTTP API server
- Launches background worker thread for processing

---

### **2. Server (`server.py`)**

The HTTP API server that handles all requests:

```python
# Key endpoints:
POST /prompt          # Queue a workflow for execution
GET  /history/{id}    # Get execution results
GET  /view            # Get generated image
GET  /system_stats    # Server health/stats
WS   /ws              # WebSocket for real-time updates
```

**Request Flow:**
```
Client Request → server.py → Queue → Worker Thread → Execution → Response
```

---

### **3. Execution Engine (`execution.py`)**

Executes workflows in the background:

```python
class PromptExecutor:
    def execute(prompt, prompt_id, extra_data, execute_outputs):
        # 1. Parse workflow JSON
        # 2. Build execution graph
        # 3. Resolve dependencies (which nodes need to run first)
        # 4. Execute nodes in correct order
        # 5. Cache results
        # 6. Return generated images
```

**Key Features:**
- **Smart Caching**: Only re-executes changed parts
- **Dependency Resolution**: Runs nodes in correct order
- **Memory Management**: Unloads models when not needed
- **Progress Tracking**: Reports progress via WebSocket

---

### **4. Node System (`nodes.py`)**

Defines all available processing nodes:

```python
# Example: CLIPTextEncode node
class CLIPTextEncode:
    INPUT_TYPES = {
        "required": {
            "text": (IO.STRING, {"multiline": True}),
            "clip": (IO.CLIP)
        }
    }
    RETURN_TYPES = (IO.CONDITIONING,)
    
    def encode(self, clip, text):
        tokens = clip.tokenize(text)
        return (clip.encode_from_tokens(tokens),)
```

**Built-in Nodes:**
- `CheckpointLoaderSimple` - Load AI models
- `CLIPTextEncode` - Convert text to embeddings
- `KSampler` - Generate images from latent space
- `VAEDecode` - Convert latent to image
- `SaveImage` - Save generated image
- And 100+ more nodes

---

## 🎨 How Image Generation Works

### **Step-by-Step Process:**

```
1. USER SUBMITS PROMPT
   ├─> Workflow JSON sent to POST /prompt
   └─> Assigned a unique prompt_id

2. WORKFLOW QUEUED
   ├─> Added to PromptQueue
   └─> Worker thread picks it up

3. WORKFLOW PARSING
   ├─> Parse JSON workflow
   ├─> Identify all nodes and connections
   └─> Build dependency graph

4. EXECUTION ORDER DETERMINED
   ├─> Topological sort of nodes
   └─> Nodes with no dependencies run first

5. NODE EXECUTION (in order):
   
   Node 4: CheckpointLoaderSimple
   ├─> Load model file (e.g., flux1-schnell.safetensors)
   ├─> Returns: [model, clip, vae]
   
   Node 6: CLIPTextEncode (positive prompt)
   ├─> Takes: text="a beautiful sunset", clip from Node 4
   ├─> Tokenize text
   ├─> Generate embeddings
   └─> Returns: conditioning tensor
   
   Node 7: CLIPTextEncode (negative prompt)
   ├─> Takes: text="bad quality", clip from Node 4
   ├─> Generate negative conditioning
   └─> Returns: negative conditioning tensor
   
   Node 5: EmptyLatentImage
   ├─> Create empty latent space (1024x1024)
   └─> Returns: latent tensor
   
   Node 3: KSampler
   ├─> Takes: model, positive, negative, latent
   ├─> Run diffusion steps (4 for FLUX-schnell)
   ├─> Gradually denoise latent
   └─> Returns: generated latent
   
   Node 8: VAEDecode
   ├─> Takes: latent from Node 3, vae from Node 4
   ├─> Decode latent to pixel space
   └─> Returns: PIL Image
   
   Node 9: SaveImage
   ├─> Takes: image from Node 8
   ├─> Save to output/ folder
   └─> Returns: {filename, subfolder, type}

6. RESULTS STORED
   ├─> Images saved to disk
   ├─> Metadata stored in history
   └─> Client notified via WebSocket

7. CLIENT RETRIEVES IMAGE
   ├─> Check /history/{prompt_id} for completion
   ├─> Get image info from outputs
   └─> Download via /view?filename=...
```

---

## 🔌 API System

### **1. Queue Prompt API**

```python
POST http://localhost:8188/prompt

Request:
{
  "prompt": {
    "3": { "class_type": "KSampler", "inputs": {...} },
    "4": { "class_type": "CheckpointLoaderSimple", "inputs": {...} },
    ...
  },
  "client_id": "unique-client-id",
  "prompt_id": "unique-prompt-id"  // optional
}

Response:
{
  "prompt_id": "abc123",
  "number": 1,
  "node_errors": {}
}
```

### **2. Get History API**

```python
GET http://localhost:8188/history/{prompt_id}

Response:
{
  "abc123": {
    "outputs": {
      "9": {
        "images": [{
          "filename": "flux_output_00001.png",
          "subfolder": "",
          "type": "output"
        }]
      }
    },
    "prompt": {...},
    "status": {"completed": true}
  }
}
```

### **3. Get Image API**

```python
GET http://localhost:8188/view?filename=flux_output_00001.png&type=output

Response: Binary image data (PNG)
```

### **4. WebSocket API**

```python
WS ws://localhost:8188/ws?clientId={client_id}

Messages received:
{
  "type": "executing",
  "data": {
    "node": "3",  // Current node being executed
    "prompt_id": "abc123"
  }
}

{
  "type": "progress",
  "data": {
    "value": 2,
    "max": 4,  // Step 2 of 4
    "prompt_id": "abc123"
  }
}

{
  "type": "executed",
  "data": {
    "node": "9",
    "output": {"images": [...]},
    "prompt_id": "abc123"
  }
}
```

---

## 📋 Workflow Structure

### **Anatomy of a Workflow JSON**

```json
{
  "NODE_ID": {
    "class_type": "NodeClassName",
    "inputs": {
      "param_name": "value",
      "connected_input": ["SOURCE_NODE_ID", OUTPUT_INDEX]
    }
  }
}
```

### **Example: Complete FLUX Workflow**

```json
{
  "4": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "flux1-schnell.safetensors"
    }
  },
  "6": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "a beautiful sunset",
      "clip": ["4", 1]  // Take output #1 from node 4
    }
  },
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 42,
      "steps": 4,
      "model": ["4", 0],      // Model from node 4, output 0
      "positive": ["6", 0],   // Conditioning from node 6
      "negative": ["7", 0],   // Conditioning from node 7
      "latent_image": ["5", 0]
    }
  }
}
```

### **Node Connection Format**

```json
"input_name": ["source_node_id", output_index]

// Examples:
"model": ["4", 0]     // Get first output of node 4
"clip": ["4", 1]      // Get second output of node 4
"vae": ["4", 2]       // Get third output of node 4
```

---

## 🧩 Node System

### **How Nodes Work**

Every node is a Python class with:

1. **INPUT_TYPES** - Defines what inputs the node accepts
2. **RETURN_TYPES** - Defines what the node outputs
3. **Function** - The actual processing logic

### **Example: Complete Node Definition**

```python
class KSampler(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffff}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "latent_image": ("LATENT",),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0})
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "sample"
    CATEGORY = "sampling"
    
    def sample(self, model, seed, steps, cfg, sampler_name, scheduler,
               positive, negative, latent_image, denoise=1.0):
        # Actual sampling logic here
        return (samples,)
```

### **Common Node Types**

| Category | Nodes | Purpose |
|----------|-------|---------|
| **Loaders** | CheckpointLoaderSimple, VAELoader | Load models from disk |
| **Conditioning** | CLIPTextEncode, ConditioningCombine | Process prompts |
| **Latent** | EmptyLatentImage, LatentUpscale | Work with latent space |
| **Sampling** | KSampler, KSamplerAdvanced | Generate images |
| **Image** | VAEDecode, VAEEncode | Convert latent ↔ image |
| **Output** | SaveImage, PreviewImage | Save/display results |

---

## ⚙️ Execution Flow

### **Detailed Execution Process**

```python
# 1. RECEIVE REQUEST
POST /prompt → server.py → PromptQueue.put()

# 2. WORKER PICKS UP JOB
prompt_worker thread:
  queue_item = PromptQueue.get()
  prompt = queue_item["prompt"]
  prompt_id = queue_item["prompt_id"]

# 3. CREATE EXECUTOR
executor = PromptExecutor(server_instance)

# 4. EXECUTE WORKFLOW
executor.execute(prompt, prompt_id):
  
  # 4.1 Parse workflow
  workflow = DynamicPrompt(prompt)
  
  # 4.2 Build execution list (dependency order)
  execution_list = workflow.get_execution_list()
  # Result: [4, 5, 6, 7, 3, 8, 9]
  
  # 4.3 Execute each node
  for node_id in execution_list:
    # Get node info
    node = workflow.get_node(node_id)
    class_type = node["class_type"]
    class_def = NODE_CLASS_MAPPINGS[class_type]
    
    # Prepare inputs
    input_data = get_input_data(node["inputs"])
    
    # Execute node
    output = class_def.FUNCTION(**input_data)
    
    # Store output for dependent nodes
    outputs_cache[node_id] = output
    
    # Send progress via WebSocket
    server.send_sync("executing", {
      "node": node_id,
      "prompt_id": prompt_id
    })

# 5. STORE RESULTS
history[prompt_id] = {
  "prompt": prompt,
  "outputs": outputs_cache,
  "status": {"completed": True}
}

# 6. NOTIFY CLIENT
server.send_sync("executed", {
  "prompt_id": prompt_id,
  "output": outputs_cache
})
```

### **Caching System**

```python
# ComfyUI only re-executes changed nodes:

First run: [4, 5, 6, 7, 3, 8, 9] ← All nodes executed

Second run (only changed prompt text):
  Node 6 changed → Cache invalidated for 6, 3, 8, 9
  Execute: [6, 3, 8, 9]
  Reuse cache: [4, 5, 7]
```

---

## 🔗 How Our Implementation Works

### **Our Notebook Implementation (`notebook_comfyui_api.py`)**

```python
# 1. START COMFYUI IN BACKGROUND
start_comfyui():
  subprocess.Popen([
    "python", "/root/ComfyUI/main.py",
    "--listen", "0.0.0.0",
    "--port", "8188"
  ])
  
  # Wait for ComfyUI to be ready
  while True:
    try:
      response = requests.get("http://localhost:8188/system_stats")
      if response.status_code == 200:
        break  # ComfyUI is ready!
    except:
      time.sleep(2)

# 2. CREATE FLASK API WRAPPER
@app.route('/generate', methods=['POST'])
def generate():
  # Get user prompt
  prompt_text = request.json["prompt"]
  
  # Load workflow template
  workflow = DEFAULT_WORKFLOW.copy()
  
  # Update prompt in workflow
  workflow["6"]["inputs"]["text"] = prompt_text
  
  # Queue to ComfyUI
  response = requests.post(
    "http://localhost:8188/prompt",
    json={"prompt": workflow, "client_id": client_id}
  )
  prompt_id = response.json()["prompt_id"]
  
  # Wait for completion via WebSocket or polling
  image_info = wait_for_completion(prompt_id)
  
  # Download generated image
  image_data = requests.get(
    f"http://localhost:8188/view",
    params={
      "filename": image_info["filename"],
      "type": image_info["type"]
    }
  ).content
  
  # Return PNG to user
  return send_file(BytesIO(image_data), mimetype="image/png")

# 3. START PUBLIC URL (ngrok)
ngrok.connect(5000)  # Expose Flask API to internet
```

### **Request Flow in Our Implementation**

```
User Request
  ↓
POST https://ngrok-url/generate {"prompt": "sunset"}
  ↓
Flask API (notebook_comfyui_api.py)
  ↓
Update workflow JSON with prompt
  ↓
POST http://localhost:8188/prompt
  ↓
ComfyUI Server (server.py)
  ↓
Queue → Worker → Executor
  ↓
Execute workflow nodes: 4→5→6→7→3→8→9
  ↓
Save image to /root/ComfyUI/output/
  ↓
History updated with image info
  ↓
Flask API polls GET /history/{prompt_id}
  ↓
Flask API downloads image via GET /view
  ↓
Flask API returns PNG to user
  ↓
User receives generated image!
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     USER REQUEST                        │
│   POST /generate {"prompt": "a beautiful sunset"}      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              FLASK API (Port 5000)                      │
│  - Receives user request                                │
│  - Updates workflow template                            │
│  - Forwards to ComfyUI                                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            COMFYUI SERVER (Port 8188)                   │
│  POST /prompt → Queue workflow                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              PROMPT QUEUE                               │
│  - Queue: [workflow1, workflow2, ...]                   │
│  - Worker thread picks up jobs                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           WORKFLOW EXECUTOR                             │
│                                                         │
│  [4] CheckpointLoaderSimple                            │
│       ↓ (model, clip, vae)                             │
│  [6] CLIPTextEncode (positive)                         │
│       ↓ (conditioning)                                  │
│  [7] CLIPTextEncode (negative)                         │
│       ↓ (conditioning)                                  │
│  [5] EmptyLatentImage                                  │
│       ↓ (latent)                                        │
│  [3] KSampler                                          │
│       ↓ (generated latent)                             │
│  [8] VAEDecode                                         │
│       ↓ (image)                                         │
│  [9] SaveImage                                         │
│       ↓ (filename, path)                               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              HISTORY & OUTPUT                           │
│  - history[prompt_id] = {outputs, status}               │
│  - /root/ComfyUI/output/flux_output_00001.png           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│          FLASK API RETRIEVES IMAGE                      │
│  GET /history/{id} → Get image metadata                │
│  GET /view?filename=... → Download image                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              RETURN TO USER                             │
│  Response: PNG image (binary data)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

1. **ComfyUI is a Graph Execution Engine**
   - Workflows = JSON graphs
   - Nodes = Processing units
   - Edges = Data flow

2. **Smart Execution**
   - Only runs what's needed
   - Caches unchanged nodes
   - Resolves dependencies automatically

3. **API-Driven**
   - HTTP REST API
   - WebSocket for real-time updates
   - Simple JSON request/response

4. **Our Implementation**
   - Wraps ComfyUI in Flask API
   - Simplifies workflow generation
   - Exposes via public URL (ngrok)

---

## 📚 Further Reading

- **ComfyUI Main Repo**: https://github.com/comfyanonymous/ComfyUI
- **ComfyUI Examples**: https://comfyanonymous.github.io/ComfyUI_examples/
- **API Script Examples**: `ComfyUI/script_examples/`

---

**Made with ❤️ for understanding AI image generation**

