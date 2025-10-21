# 🎨 AI Image Generator - Web Interface Guide

Beautiful web interface for your FLUX.1-Krea-dev image generation API!

## 🚀 Quick Start

### Step 1: Download the Web Interface

```bash
# Download from GitHub
wget https://raw.githubusercontent.com/kwnsgsuksbdhdjdkd/modalrun/main/web_interface.html
```

Or just open this URL in your browser:
```
https://raw.githubusercontent.com/kwnsgsuksbdhdjdkd/modalrun/main/web_interface.html
```

Right-click and "Save As..." to download.

### Step 2: Open in Browser

Simply double-click `web_interface.html` to open it in your browser!

That's it! No installation, no server needed!

---

## 🎯 How to Use

### 1. **Enter Your API URL**
   - The web page has your ngrok URL pre-filled
   - If it changes, just update it in the input field
   - It will be saved automatically for next time

### 2. **Write Your Prompt**
   - Type what image you want to generate
   - Or click one of the example prompts
   - Press Enter or click "Generate Image"

### 3. **Wait for Generation**
   - A loading bar will show progress
   - Generation takes 40-70 seconds
   - The button will be disabled during generation

### 4. **View & Download**
   - Your image will appear below
   - Click "Download Image" to save it
   - Generate time and prompt are shown

---

## ✨ Features

### 🎨 Beautiful Design
- Modern gradient design
- Responsive (works on mobile!)
- Smooth animations
- Professional look

### 🚀 Easy to Use
- One-click example prompts
- Auto-save API URL
- Enter key to generate
- Clear button to reset

### ⚡ Smart Features
- Loading states
- Error messages
- Generation timer
- Download button
- Prompt history shown

### 📱 Mobile Friendly
- Responsive design
- Touch-friendly buttons
- Adapts to screen size

---

## 💡 Example Prompts

```
a cute cat wearing sunglasses on a beach at sunset

A futuristic cityscape with flying cars and neon lights, cyberpunk style

A magical forest with glowing mushrooms and fairy lights, fantasy art

A hyper-realistic portrait of a robot reading a book in a cozy library

A beautiful landscape with mountains, a lake, and aurora borealis in the sky
```

---

## 🔧 Customization

### Change API URL
1. Edit the `value` in the API URL input field
2. It will be saved automatically in your browser

### Add Your Own Example Prompts
Edit `web_interface.html` and find this section:

```html
<div class="example-prompts">
    <div class="example-prompt" onclick="setPrompt(this.textContent)">
        Your custom prompt here
    </div>
</div>
```

### Change Colors
Edit the CSS gradients in the `<style>` section:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Change `#667eea` and `#764ba2` to your preferred colors!

---

## 🌐 Sharing with Others

### Option 1: Direct File
- Send the HTML file to anyone
- They open it in their browser
- They enter your API URL
- They can generate images!

### Option 2: Host on GitHub Pages
1. Create a new repository
2. Upload `web_interface.html` and rename to `index.html`
3. Enable GitHub Pages in Settings
4. Share the URL: `https://yourusername.github.io/reponame`

### Option 3: Host on Netlify (Free)
1. Go to netlify.com
2. Drag and drop the HTML file
3. Get instant URL
4. Share with anyone!

---

## 🔒 Security Notes

⚠️ **Important:**
- Your ngrok URL is exposed in the web page
- Anyone with the file can see your API URL
- Ngrok URLs are public but temporary
- For production, use authentication!

### Add Password Protection (Simple)

Add this at the top of the `<script>` section:

```javascript
const API_PASSWORD = "your-secret-password";

async function generateImage() {
    const password = prompt("Enter password:");
    if (password !== API_PASSWORD) {
        alert("Wrong password!");
        return;
    }
    // ... rest of the code
}
```

---

## 🐛 Troubleshooting

### Images Not Loading
- Check that your Modal notebook is running
- Verify the API URL is correct
- Check browser console (F12) for errors
- Make sure ngrok is connected

### CORS Errors
- Your API already has CORS enabled
- If you get errors, your API might be down
- Restart the Modal notebook

### Slow Generation
- FLUX models take 40-70 seconds
- First generation is slower (model loading)
- Subsequent generations are faster (cached)

### Button Stays Disabled
- Refresh the page
- Check browser console for errors
- API might have crashed - restart it

---

## 📊 Technical Details

### Stack
- **HTML5** - Structure
- **CSS3** - Styling with gradients and animations
- **JavaScript** (Vanilla) - No frameworks needed!
- **Fetch API** - HTTP requests
- **Blob API** - Image handling

### Browser Compatibility
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

### File Size
- Single file: ~15KB
- No dependencies
- No build process
- No external libraries

---

## 🎯 Advanced Usage

### Integrate with Your Website

```html
<!-- Add to your existing website -->
<iframe 
    src="web_interface.html" 
    width="100%" 
    height="1000px"
    frameborder="0"
></iframe>
```

### Embed API Calls in Your App

```javascript
async function generateImage(prompt) {
    const response = await fetch('YOUR_API_URL/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt })
    });
    
    const blob = await response.blob();
    return URL.createObjectURL(blob);
}
```

### Queue Multiple Requests

```javascript
const prompts = [
    "a cat",
    "a dog", 
    "a bird"
];

for (const prompt of prompts) {
    await generateImage(prompt);
}
```

---

## 📝 Changelog

### v1.0 (Current)
- ✅ Initial release
- ✅ Single-file interface
- ✅ Example prompts
- ✅ Download functionality
- ✅ Auto-save API URL
- ✅ Mobile responsive
- ✅ Loading states
- ✅ Error handling

### Future Ideas
- 📋 Prompt history
- 🎨 Image gallery
- ⚙️ Advanced settings (steps, CFG, seed)
- 💾 Save favorites
- 🔄 Regenerate with same prompt
- 📤 Share to social media

---

## ❤️ Credits

- **FLUX.1-Krea-dev** - AI Model
- **ComfyUI** - Backend framework
- **Modal** - Notebook hosting
- **ngrok** - Public URL tunneling

---

## 📞 Support

Having issues? Check:
1. Is your Modal notebook running?
2. Is the API URL correct?
3. Is ngrok connected?
4. Check browser console (F12)

Still stuck? Share your error message!

---

**Enjoy generating beautiful images! 🎨✨**
