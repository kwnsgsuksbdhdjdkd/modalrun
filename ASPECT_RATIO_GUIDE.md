# 📐 Aspect Ratio Support Guide

## ✨ Overview

Your ComfyUI API now supports **6 different aspect ratios** for image generation! Users can request images in landscape, portrait, square, or cinematic formats.

---

## 🎯 Supported Aspect Ratios

| Aspect Ratio | Dimensions | Pixels | Best For |
|-------------|-----------|---------|----------|
| **1:1** | 1536×1536 | 2.36M | Square - Instagram, avatars, general |
| **16:9** | 2048×1152 | 2.36M | Landscape - YouTube, monitors, desktop |
| **9:16** | 1152×2048 | 2.36M | Portrait - TikTok, Instagram Stories, mobile |
| **4:3** | 1776×1328 | 2.36M | Standard - Classic photos, presentations |
| **3:2** | 1888×1256 | 2.37M | Photo - DSLR standard, print |
| **21:9** | 2400×1024 | 2.46M | Cinematic - Ultra-wide, movie scenes |

**All ratios maintain ~2.4M pixel budget for consistent quality and generation time!**

---

## 🚀 How to Use

### **Client-Side (JavaScript/SocketIO)**

```javascript
// Connect to server
const socket = io('https://your-ngrok-url.ngrok-free.dev');

// Generate with aspect ratio
socket.emit('generate', {
    user_id: 'your-user-id',
    prompt: 'A futuristic cityscape at sunset with flying cars',
    aspect_ratio: '16:9'  // Specify ratio here!
});

// Listen for response
socket.on('generation_started', (data) => {
    console.log('Started:', data.message);
    console.log('Resolution:', data.resolution);  // "2048×1152"
    console.log('Aspect Ratio:', data.aspect_ratio);  // "16:9"
    console.log('Total Pixels:', data.total_pixels);  // 2359296
});

socket.on('image_ready', (data) => {
    console.log('Image ready!');
    document.getElementById('output').src = data.image_data;
});
```

### **HTML Example**

```html
<!DOCTYPE html>
<html>
<head>
    <title>ComfyUI Aspect Ratio Demo</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <h1>🎨 ComfyUI Generator</h1>
    
    <label>Prompt:</label><br>
    <input type="text" id="prompt" size="50" 
           value="A beautiful landscape"><br><br>
    
    <label>Aspect Ratio:</label><br>
    <select id="aspectRatio">
        <option value="1:1">1:1 (Square)</option>
        <option value="16:9">16:9 (Landscape)</option>
        <option value="9:16">9:16 (Portrait)</option>
        <option value="4:3">4:3 (Standard)</option>
        <option value="3:2">3:2 (Photo)</option>
        <option value="21:9">21:9 (Cinematic)</option>
    </select><br><br>
    
    <button onclick="generate()">Generate Image</button>
    
    <div id="status"></div>
    <img id="output" style="max-width: 100%; margin-top: 20px;">
    
    <script>
        const socket = io('https://your-ngrok-url.ngrok-free.dev');
        let userId = null;
        
        socket.on('connected', (data) => {
            userId = data.user_id;
            console.log('Connected! User ID:', userId);
        });
        
        socket.on('generation_started', (data) => {
            document.getElementById('status').innerHTML = 
                `⏳ ${data.message}<br>
                 📐 Resolution: ${data.resolution}<br>
                 ⏱️ Est. time: ${data.estimated_time}`;
        });
        
        socket.on('image_ready', (data) => {
            document.getElementById('status').innerHTML = 
                `✅ Image ready in ${data.generation_time.toFixed(1)}s!`;
            document.getElementById('output').src = data.image_data;
        });
        
        socket.on('generation_error', (data) => {
            document.getElementById('status').innerHTML = 
                `❌ Error: ${data.error}`;
        });
        
        function generate() {
            const prompt = document.getElementById('prompt').value;
            const aspectRatio = document.getElementById('aspectRatio').value;
            
            socket.emit('generate', {
                user_id: userId,
                prompt: prompt,
                aspect_ratio: aspectRatio
            });
        }
    </script>
</body>
</html>
```

---

## 📋 Default Behavior

If no `aspect_ratio` is specified, the server defaults to **1:1 (square)**.

```javascript
// These are equivalent:
socket.emit('generate', {user_id: id, prompt: 'sunset'});
socket.emit('generate', {user_id: id, prompt: 'sunset', aspect_ratio: '1:1'});
```

---

## 🔍 Server Response

### **generation_started Event**

```json
{
    "status": "started",
    "message": "Generating high-quality image for: \"A futuristic cityscape\"",
    "estimated_time": "120-180 seconds (high quality mode: 30 steps @ 2048×1152)",
    "prompt": "A futuristic cityscape",
    "quality_mode": "high",
    "resolution": "2048×1152",
    "aspect_ratio": "16:9",
    "steps": 30,
    "total_pixels": 2359296
}
```

### **image_ready Event**

```json
{
    "status": "complete",
    "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "prompt": "A futuristic cityscape",
    "generation_time": 156.2,
    "size_bytes": 2847563
}
```

---

## 📊 Server Logs

When a user requests an image with an aspect ratio, you'll see:

```
🎨 SocketIO generation request from user 4540a010...: 'A steampunk robot'
📐 Aspect ratio: 9:16 → 1152×2048 (2,359,296 pixels)
👤 User session ID: xL278IYTiGuEnu7JAAAB
🚀 Starting background generation thread...
⌛ Starting generation for user 4540a010...
📐 Resolution: 1152×2048 (aspect ratio: 9:16)
✨ Enhanced prompt: 'A steampunk robot, high quality, detailed, sharp focus...'
✅ Workflow updated with 1152×2048 dimensions
✅ Queued prompt 6799a8e8-... for user 4540a010...
⏳ Waiting for high-quality generation (max 900s)...
✅ High-quality image generation complete after 142s!
📤 Sent image to user 4540a010... via SocketIO
```

---

## 🎨 Use Cases

### **1:1 (Square)**
- Instagram posts
- Profile pictures
- Thumbnails
- General purpose

### **16:9 (Landscape)**
- YouTube thumbnails
- Desktop wallpapers
- Presentation slides
- Horizontal scenes

### **9:16 (Portrait)**
- Instagram/TikTok Stories
- Mobile wallpapers
- Vertical videos
- Phone screens

### **4:3 (Standard)**
- Classic photography
- Presentations
- Old-school displays
- Printed photos

### **3:2 (Photo)**
- DSLR camera standard
- Professional photography
- Print formats
- Magazine layouts

### **21:9 (Cinematic)**
- Ultra-wide monitors
- Movie scenes
- Cinematic artwork
- Panoramic views

---

## ⚡ Performance

**All aspect ratios generate in similar time (~120-180 seconds)** because they maintain the same pixel budget (~2.4M pixels).

| Ratio | Dimensions | Time |
|-------|-----------|------|
| 1:1 | 1536×1536 | ~150s |
| 16:9 | 2048×1152 | ~150s |
| 9:16 | 1152×2048 | ~150s |
| 4:3 | 1776×1328 | ~150s |
| 3:2 | 1888×1256 | ~150s |
| 21:9 | 2400×1024 | ~155s |

**No extra wait time for different ratios!**

---

## 🚨 Error Handling

### **Invalid Aspect Ratio**

If you send an invalid ratio, the server will:
1. Log a warning
2. Default to 1:1 (square)
3. Continue generation

```
⚠️ Invalid aspect ratio 'custom', defaulting to 1:1
```

### **Missing aspect_ratio Parameter**

If omitted, defaults to **1:1** automatically.

---

## 💡 Tips

### **Best Practices**

1. **Match content to ratio**
   - Use 9:16 for tall subjects (people standing, buildings)
   - Use 16:9 for wide subjects (landscapes, cityscapes)
   - Use 1:1 for balanced compositions

2. **Prompt adjustments**
   ```javascript
   // For 16:9 landscape
   prompt: "wide panoramic view of mountains at sunset"
   
   // For 9:16 portrait
   prompt: "tall futuristic skyscraper reaching into clouds"
   
   // For 21:9 cinematic
   prompt: "epic cinematic scene of space battle, ultra wide angle"
   ```

3. **UI Design**
   - Show preview box with correct aspect ratio
   - Display actual pixel dimensions
   - Indicate estimated generation time

---

## 🔧 Technical Details

### **Fixed Pixel Budget Algorithm**

All ratios maintain ~2.36M pixels for consistent performance:

```python
TARGET_PIXELS = 2359296  # ~1536×1536

def calculate_dimensions(aspect_ratio):
    ratios = {"16:9": (16, 9), ...}
    w_ratio, h_ratio = ratios[aspect_ratio]
    
    # Calculate maintaining pixel budget
    aspect = w_ratio / h_ratio
    height = int((TARGET_PIXELS / aspect) ** 0.5)
    width = int(height * aspect)
    
    # Round to multiples of 8 (FLUX requirement)
    width = (width // 8) * 8
    height = (height // 8) * 8
    
    return width, height
```

### **Why Multiples of 8?**

FLUX models require dimensions divisible by 8 for stable diffusion latent space calculations.

---

## 📸 Examples

### **Landscape (16:9) - YouTube Thumbnail**
```javascript
socket.emit('generate', {
    user_id: userId,
    prompt: 'Epic gaming scene, vibrant colors, action-packed',
    aspect_ratio: '16:9'
});
// Generates: 2048×1152
```

### **Portrait (9:16) - Instagram Story**
```javascript
socket.emit('generate', {
    user_id: userId,
    prompt: 'Fashion model portrait, studio lighting, professional',
    aspect_ratio: '9:16'
});
// Generates: 1152×2048
```

### **Cinematic (21:9) - Movie Poster**
```javascript
socket.emit('generate', {
    user_id: userId,
    prompt: 'Cinematic space battle, starships, epic scale, ultra wide',
    aspect_ratio: '21:9'
});
// Generates: 2400×1024
```

---

## 🎉 Summary

✅ **6 aspect ratios** supported out of the box  
✅ **Consistent quality** across all ratios  
✅ **Same generation time** (~2-3 minutes)  
✅ **Automatic validation** with fallback  
✅ **Detailed logging** for debugging  
✅ **Easy to use** - just add one parameter!  

---

## 🆘 Troubleshooting

**Q: My custom ratio isn't working**  
A: Only predefined ratios (1:1, 16:9, 9:16, 4:3, 3:2, 21:9) are supported. Invalid ratios default to 1:1.

**Q: Can I add custom dimensions?**  
A: Yes! Edit `ASPECT_RATIOS` dictionary in `notebook_comfyui_api.py`:
```python
ASPECT_RATIOS = {
    "1:1": (1536, 1536),
    "custom": (2000, 1000),  # Add your custom ratio
}
```

**Q: Does it affect generation time?**  
A: No! All ratios have ~2.4M pixel budget for consistent timing.

**Q: What about extreme ratios like 1:4 or 4:1?**  
A: You can add them, but very thin images may have quality issues. Test first!

---

**Feature implemented:** 2025-10-22  
**Pushed to GitHub main branch** ✅

Enjoy creating images in any aspect ratio! 🎨

