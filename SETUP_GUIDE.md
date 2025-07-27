# Security Screening System - Setup Guide

## Current Status: ✅ WORKING!

Your security screening system with status messages is now working in **Basic Mode**.

## Quick Start

### **Run Basic Version (Working Now)**

```powershell
python main_basic.py
```

**What it includes:**

- ✅ Status message system (the feature you requested)
- ✅ Basic face detection using OpenCV
- ✅ Real-time status updates with color coding
- ✅ Professional GUI with status area
- ✅ Detection logging and timers

**What's missing:**

- ❌ Advanced face recognition (requires face-recognition library)
- ❌ Person identification by name
- ❌ Email/SMS alerts

## Upgrade to Full Version

### **Step 1: Install CMake**

1. Go to https://cmake.org/download/
2. Download "Windows x64 Installer"
3. **IMPORTANT**: During installation, check "Add CMake to system PATH"
4. Restart PowerShell/terminal

### **Step 2: Install Face Recognition**

```powershell
# After installing CMake and restarting terminal
cmake --version  # Should work now
python -m pip install face-recognition
```

### **Step 3: Run Full Version**

```powershell
python main.py
```

## Status Messages Demo

To see all possible status messages:

```powershell
python status_demo.py
```

## Features Comparison

| Feature          | Basic Mode | Full Mode |
| ---------------- | ---------- | --------- |
| Status Messages  | ✅         | ✅        |
| Face Detection   | ✅         | ✅        |
| Face Recognition | ❌         | ✅        |
| Person Names     | ❌         | ✅        |
| Email/SMS Alerts | ❌         | ✅        |
| Security Logging | ✅         | ✅        |

## Status Messages in Action

The system now displays real-time status messages:

- 🟢 **"System ready - Please position yourself in front of the camera"**
- 🟡 **"👁️ Scanning for faces... Please position yourself in front of the camera"**
- 🟠 **"⚠️ Multiple faces detected - Please ensure only one person is in frame"**
- 🔵 **"🔍 Face detected - Basic detection mode"**
- 🟠 **"⏱️ Please stand still for X seconds - Processing..."**
- 🟢 **"✅ SCAN COMPLETE: Basic face detection completed"**

## Troubleshooting

### "cv2 not found"

```powershell
python -m pip install opencv-python
```

### "tkinter not found"

```powershell
python -m pip install tk
```

### CMake Issues

- Download from cmake.org (official source)
- Make sure to add to PATH during installation
- Restart terminal after installation

## Success! 🎉

Your **centralized status message system** is now implemented and working! The main goal of improving user experience with real-time feedback has been achieved.
