# RLProfilePicturesREVAMP - BakkesMod Plugin

> C++ plugin for BakkesMod that enables custom profile pictures and cross-platform avatar viewing in Rocket League.

## 🎯 Overview

This plugin hooks into Rocket League via BakkesMod to:
- Display custom avatars for Epic Games users
- Fetch and display avatars from Steam, PSN, Xbox, and Switch
- Provide an ImGui-based settings interface

## 🏗️ Architecture

```
RLProfilePicturesREVAMP/
├── IMGUI/                  # Dear ImGui library (DirectX 11 backend)
│   ├── imgui.cpp
│   ├── imgui_impl_dx11.cpp
│   └── ...
├── RLSDK/                  # Rocket League SDK (reverse-engineered headers)
│   └── SDK_HEADERS/
│       ├── Engine_classes.cpp
│       ├── TAGame_classes.cpp
│       └── ...
├── Memory/
│   ├── MemoryHelper.h      # Memory reading utilities
│   └── MemoryHelper.cpp    # Pattern scanning implementation
├── Config/
│   └── Constants.h         # Configuration constants
└── RLProfilePicturesREVAMP.sln  # Visual Studio solution
```

## 🔧 Technical Details

### Memory Reading
The plugin uses pattern scanning to locate game data:

```cpp
// Example from MemoryHelper.cpp
uintptr_t MemoryHelper::FindPattern(const std::string& pattern) {
    // Scans process memory for byte patterns
    // Used to locate player data structures
}
```

### ImGui Integration
Custom UI rendered via DirectX 11:
- Settings panel for avatar configuration
- Image preview and brightness controls
- Platform-specific toggles

### API Communication
Communicates with the backend API for:
- Fetching platform avatars
- Uploading custom Epic avatars
- Checking for plugin updates

## 📋 Requirements

- **Visual Studio 2019/2022** with C++17 support
- **BakkesMod SDK** (auto-detected via registry)
- **Windows SDK** (DirectX 11)

## 🔨 Building

1. Open `RLProfilePicturesREVAMP.sln` in Visual Studio
2. Ensure BakkesMod is installed (SDK path is read from registry)
3. Build in Release mode for x64
4. Output DLL is automatically patched by BakkesMod SDK

```xml
<!-- From BakkesMod.props -->
<BakkesModPath>$(registry:HKEY_CURRENT_USER\Software\BakkesMod\AppPath@BakkesModPath)</BakkesModPath>
```

## 📦 Dependencies

| Library | Purpose |
|---------|---------|
| BakkesMod SDK | Plugin framework and game hooks |
| Dear ImGui | Immediate-mode GUI |
| stb_image | Image loading (PNG, JPG, GIF, etc.) |
| DirectX 11 | Graphics rendering |

## ⚠️ Important Notes

- **No longer functional**: EAC blocks this type of memory access
- **SDK Headers**: The RLSDK folder contains reverse-engineered headers from Rocket League's Unreal Engine implementation
- **Memory operations**: All memory reading is done on the local process only

## 📄 File Reference

| File | Description |
|------|-------------|
| `MemoryHelper.cpp` | Process memory access and pattern scanning |
| `imgui_impl_dx11.cpp` | DirectX 11 rendering backend for ImGui |
| `stb_image.h` | Single-header image loading library |

---

*Part of the RLProfilePicturesREVAMP project by [@borgox](https://github.com/borgox)*