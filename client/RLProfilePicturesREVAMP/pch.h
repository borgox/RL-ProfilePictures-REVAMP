#pragma once

// Windows headers must come first for proper type definitions  
#define _CRT_SECURE_NO_WARNINGS
#define NOMINMAX
#include <windows.h>
#include <algorithm>
#include <locale>
#include <stdlib.h>
#include <ctype.h>
#include <chrono>
#include <thread>

// Standard C++ headers
#include <string>
#include <vector>
#include <functional>
#include <memory>
#include <type_traits>

// BakkesMod headers
#include "bakkesmod/plugin/bakkesmodplugin.h"

// RLSDK headers 
#include "RLSDK/SdkHeaders.hpp"

// Template functions for UObject access 
template<typename T>
T* GetInstanceOf() {
    if (std::is_base_of<UObject, T>::value && UObject::GObjObjects()) {
        for (int32_t i = (UObject::GObjObjects()->size() - 1); i > 0; i--) {
            UObject* uObject = UObject::GObjObjects()->at(i);
            if (uObject && uObject->IsA<T>()) {
                if (uObject->GetFullName().find("Default__") == std::string::npos) {
                    return static_cast<T*>(uObject);
                }
            }
        }
    }
    return nullptr;
}

template<typename T>
inline T* Cast(UObject* obj) {
    if (!obj || !obj->IsA<T>()) // || !obj->IsValid()
        return nullptr;
    return static_cast<T*>(obj);
}

// IMGUI headers after BakkesMod
#include "IMGUI/imgui.h"
#include "IMGUI/imgui_stdlib.h"
#include "IMGUI/imgui_searchablecombo.h"
#include "IMGUI/imgui_rangeslider.h"

#include "logging.h"

// RLProfilePicturesREVAMP headers
#include "Config/Constants.h"
#include "Utils/Logger.h"
#include "Utils/FileUtils.h"
#include "Utils/StringUtils.h"
#include "Memory/MemoryHelper.h"
#include "RocketLeague/RLObjects.h"
#include "Avatar/ImageProcessor.h"
#include "Avatar/AvatarDownloader.h"
#include "Avatar/AvatarManager.h"
#include "UI/SettingsUI.h"