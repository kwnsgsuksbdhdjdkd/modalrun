# 🔍 SocketIO Debugging Guide

## Issue: generate_image Event Not Received

### What Was Wrong

The `generate_image` event was not being received by the server even though connections were working.

### Root Cause

Possible causes:
1. **Client not sending data correctly** - Missing `user_id` or `prompt`
2. **Event name mismatch** - Client using different event name
3. **Data format issues** - Client not sending as JSON object
4. **Silent failures** - No error logging to identify the problem

### What We Fixed

✅ **Added Comprehensive Logging**
- Log raw event reception
- Log data type and content
- Log user session tracking
- Log acknowledgments sent

✅ **Added Data Validation**
- Check if data exists
- Check if data is a dict
- Check if user_id is present
- Send error messages back to client

✅ **Added Error Handling**
- Try-catch blocks around all handlers
- Full exception tracebacks logged
- Error events sent to clients

✅ **Better Debugging**
- Connection count tracking
- Session ID logging
- Acknowledgment logging

---

## How to Debug

### Step 1: Check Server Logs

When you restart your Modal notebook, you should see:

```
✅ WebSocket connected: User abb58184... (sid: vFZhK1ab3tcOFlbCAAAb)
📊 Total connected users: 1
```

### Step 2: Send a generate_image Event

From your client, emit:

```javascript
socket.emit('generate_image', {
  user_id: userId,  // MUST be the user_id you received on 'connected'
  prompt: 'a beautiful sunset'
});
```

### Step 3: Watch for These Logs

You should see:

```
🔔 RAW EVENT RECEIVED: generate_image
📦 Raw data received: {'user_id': 'abb58184-...', 'prompt': 'a beautiful sunset'}
📦 Data type: <class 'dict'>
🎨 SocketIO generation request from user abb58184...: 'a beautiful sunset'
👤 User session ID: vFZhK1ab3tcOFlbCAAAb
✅ Sent generation_started acknowledgment to user abb58184...
```

---

## Common Issues & Solutions

### ❌ Issue: "No data received in generate_image event"

**Cause:** Client not sending any data

**Solution:**
```javascript
// ❌ Wrong
socket.emit('generate_image');

// ✅ Correct
socket.emit('generate_image', {
  user_id: userId,
  prompt: 'your prompt here'
});
```

---

### ❌ Issue: "Missing user_id"

**Cause:** Not including user_id or using wrong variable

**Solution:**
```javascript
// First, store the user_id when you connect
socket.on('connected', (data) => {
  userId = data.user_id;  // Save this!
  console.log('My user ID:', userId);
});

// Then use it when generating
socket.emit('generate_image', {
  user_id: userId,  // Use the saved userId
  prompt: 'your prompt'
});
```

---

### ❌ Issue: "User session ID: NOT FOUND"

**Cause:** The user_id you're sending doesn't match any connected user

**Solution:**
- Make sure you're using the exact user_id from the 'connected' event
- Don't hardcode or make up a user_id
- If you disconnect and reconnect, you get a new user_id

---

### ❌ Issue: No logs at all for generate_image

**Cause:** Event name mismatch

**Solution:**
```javascript
// ❌ Wrong event name
socket.emit('generate', {...});
socket.emit('create_image', {...});

// ✅ Correct event name
socket.emit('generate_image', {...});
```

---

## Testing with the HTML Client

### Step 1: Open test_socketio_client.html

Open `test_socketio_client.html` in your browser.

### Step 2: Enter Your ngrok URL

Enter your Modal ngrok URL (e.g., `https://abc123.ngrok-free.app`)

### Step 3: Click "Connect to Server"

You should see in the logs:
```
✅ Connected! User ID: abb58184-...
```

### Step 4: Enter a Prompt and Generate

Enter a prompt like "a beautiful sunset" and click "Generate Image"

You should see in the logs:
```
📤 Sending generation request...
✅ Request sent successfully!
🎨 Generation started: ...
⏳ Progress: Image is being generated...
✅ Image ready! Generation time: 45.2s
```

---

## What the Server Will Show

In your Modal notebook logs, you'll see:

```
🔔 RAW EVENT RECEIVED: generate_image
📦 Raw data received: {'user_id': 'abb58184-...', 'prompt': 'a beautiful sunset'}
📦 Data type: <class 'dict'>
🎨 SocketIO generation request from user abb58184...: 'a beautiful sunset'
👤 User session ID: vFZhK1ab3tcOFlbCAAAb
✅ Sent generation_started acknowledgment to user abb58184...
⌛ Starting generation for user abb58184...
✅ Queued prompt 12345-... for user abb58184...
✅ Image generated in 45.2s for user abb58184...
📤 Sent image to user abb58184... via SocketIO
```

---

## Quick Checklist

✅ Is your Modal notebook running?
✅ Is ngrok connected and showing a public URL?
✅ Did you connect to the SocketIO server successfully?
✅ Did you save the user_id from the 'connected' event?
✅ Are you sending both user_id AND prompt?
✅ Is the event name exactly 'generate_image'?
✅ Are you sending a plain JavaScript object (not stringified)?

---

## Example Client Code

```javascript
const socket = io('https://your-ngrok-url.ngrok-free.app');

let userId = null;

// Step 1: Get your user_id
socket.on('connected', (data) => {
  userId = data.user_id;
  console.log('✅ Connected! User ID:', userId);
});

// Step 2: Listen for responses
socket.on('generation_started', (data) => {
  console.log('🎨 Generation started:', data.message);
});

socket.on('generation_progress', (data) => {
  console.log('⏳ Progress:', data.message);
});

socket.on('image_ready', (data) => {
  console.log('✅ Image ready!');
  // Display the image
  const img = document.createElement('img');
  img.src = data.image_data;
  document.body.appendChild(img);
});

socket.on('generation_error', (data) => {
  console.error('❌ Error:', data.message);
});

// Step 3: Send generation request
function generateImage(prompt) {
  if (!userId) {
    console.error('❌ Not connected yet!');
    return;
  }
  
  socket.emit('generate_image', {
    user_id: userId,
    prompt: prompt
  });
}

// Use it:
generateImage('a beautiful sunset over mountains');
```

---

## Still Not Working?

1. **Check the browser console** for JavaScript errors
2. **Check the Modal notebook logs** for Python errors
3. **Verify ngrok is running** and the URL is correct
4. **Try the test HTML client** first to verify the server works
5. **Check your firewall** isn't blocking WebSocket connections

---

**All fixes have been pushed to GitHub main branch!** 🎉

Restart your Modal notebook to get the latest version with full debugging.
