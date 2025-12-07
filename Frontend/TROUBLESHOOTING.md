# Frontend Troubleshooting Guide

## Issue: "This localhost page can't be found" (404 Error)

### Possible Causes:

1. **Dev server is not running**
2. **Wrong port** (should be 3000, not 3000/)
3. **Build errors preventing startup**
4. **Missing dependencies**

---

## Solution Steps:

### Step 1: Make Sure Dev Server is Running

Open a terminal and run:
```cmd
cd Frontend
npm run dev
```

You should see:
```
VITE v5.x.x  ready in XXX ms
➜  Local:   http://localhost:3000/
➜  Network: http://xxx.xxx.xxx.xxx:3000/
```

### Step 2: Check the Correct URL

- ✅ **Correct**: `http://localhost:3000` or `http://localhost:3000/`
- ❌ **Wrong**: `http://localhost:3000/dashboard` (if server isn't running)

### Step 3: Install Missing Dependencies

If you see errors about missing packages:
```cmd
cd Frontend
npm install --legacy-peer-deps
```

Or use the helper script:
```cmd
cd Frontend
START_FRONTEND.bat
```

### Step 4: Clear Cache and Restart

```cmd
cd Frontend
rmdir /s /q node_modules\.vite
npm run dev
```

### Step 5: Check for Build Errors

Look at the terminal where you ran `npm run dev`. If you see errors:

**Common Error 1: Missing Dependencies**
```
Error: Cannot find module '@mui/icons-material'
```
**Fix:**
```cmd
npm install @mui/icons-material@5.14.18 --legacy-peer-deps
```

**Common Error 2: JSX Syntax Error**
```
The JSX syntax extension is not currently enabled
```
**Fix:** Already fixed in vite.config.js

**Common Error 3: Import Errors**
```
Failed to resolve import
```
**Fix:** Check that all imported files exist

---

## Current Setup Status:

✅ **Fixed Issues:**
- JSX loader configuration
- File renamed: index.js → index.jsx
- Simplified Dashboard component
- Added missing dependencies to package.json

✅ **What Should Work:**
- Basic dashboard display
- Material-UI components
- React Router navigation
- Theme and styling

⚠️ **What Needs Backend:**
- Real-time data streams
- Action execution
- Query processing
- WebSocket connection

---

## Quick Start (Fresh Install):

```cmd
# 1. Navigate to Frontend
cd Frontend

# 2. Install dependencies
npm install --legacy-peer-deps

# 3. Start dev server
npm run dev

# 4. Open browser
# Go to: http://localhost:3000
```

---

## Verify Installation:

### Check if server is running:
```cmd
curl http://localhost:3000
```

Should return HTML, not an error.

### Check if port is in use:
```cmd
netstat -ano | findstr :3000
```

If port 3000 is already in use, you'll see output. Kill that process or change the port in vite.config.js.

---

## Still Not Working?

### 1. Check Terminal Output
Look for specific error messages in the terminal where you ran `npm run dev`

### 2. Check Browser Console
Press F12 in your browser and look at the Console tab for JavaScript errors

### 3. Verify File Structure
Make sure these files exist:
- `Frontend/src/index.jsx` ✓
- `Frontend/src/App.jsx` ✓
- `Frontend/src/components/Dashboard/SimpleDashboard.jsx` ✓
- `Frontend/public/index.html` ✓
- `Frontend/vite.config.js` ✓

### 4. Nuclear Option (Complete Reset)
```cmd
cd Frontend
rmdir /s /q node_modules
del package-lock.json
npm install --legacy-peer-deps
npm run dev
```

---

## Expected Behavior:

When working correctly:
1. Terminal shows "VITE ready" message
2. Browser shows the dashboard with:
   - "Live Data RAG with Actions" header
   - 4 stat cards (Queries, Actions, Data Points, System Status)
   - Welcome message
   - Next steps guide
   - System information panel

---

## Need More Help?

Check these files for detailed information:
- `FRONTEND_FIX.md` - JSX configuration fix
- `DEPENDENCY_FIX.md` - Dependency installation guide
- `package.json` - All dependencies and scripts
- `vite.config.js` - Vite configuration

Or check the terminal output for specific error messages!
