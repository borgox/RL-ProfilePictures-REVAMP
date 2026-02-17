#include "pch.h"
#include "FileUtils.h"
#include "../Config/Constants.h"
// windows.h is included via pch.h
#include <commdlg.h>
#include <filesystem>

// =============================================================================
// FILE UTILITIES 
// =============================================================================

namespace RLProfilePicturesFileUtils {
    
    bool EnsureTempDirectoryExists() {
        if (std::filesystem::exists(RLProfilePicturesConstants::TEMP_DIRECTORY) && 
            std::filesystem::is_directory(RLProfilePicturesConstants::TEMP_DIRECTORY)) {
            return true;
        }
        
        try {
            std::filesystem::create_directory(RLProfilePicturesConstants::TEMP_DIRECTORY);
            return true;
        } 
        catch (const std::filesystem::filesystem_error&) {
            return false;
        }
    }
    
    std::string WStringToUtf8(const std::wstring& w) {
        if (w.empty()) return {};
        int size_needed = WideCharToMultiByte(CP_UTF8, 0, w.c_str(), -1, nullptr, 0, nullptr, nullptr);
        std::string strTo(size_needed, 0);
        WideCharToMultiByte(CP_UTF8, 0, w.c_str(), -1, strTo.data(), size_needed, nullptr, nullptr);
        return strTo;
    }

    std::wstring Utf8ToWString(const std::string& str) {
        if (str.empty()) 
            return {};
        int size_needed = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), -1, nullptr, 0);
        std::wstring strTo(size_needed, 0);
        MultiByteToWideChar(CP_UTF8, 0, str.c_str(), -1, strTo.data(), size_needed);
        return strTo;
    }
    
    bool OpenImageFileDialog(std::filesystem::path& outPath) {
        wchar_t fileBuffer[MAX_PATH] = { 0 };
        
        OPENFILENAMEW ofn;
        ZeroMemory(&ofn, sizeof(ofn));
        ofn.lStructSize = sizeof(ofn);
        ofn.hwndOwner = nullptr;
        ofn.lpstrFilter =
            L"Image Files (*.png;*.jpg;*.jpeg)\0*.png;*.jpg;*.jpeg\0"
            L"PNG Files (*.png)\0*.png\0"
            L"JPEG Files (*.jpg;*.jpeg)\0*.jpg;*.jpeg\0"
            L"All Files (*.*)\0*.*\0\0";
        ofn.lpstrFile = fileBuffer;
        ofn.nMaxFile = MAX_PATH;
        ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_HIDEREADONLY;
        ofn.lpstrDefExt = L"png";
        
        if (GetOpenFileNameW(&ofn) == TRUE) {
            outPath = fileBuffer;
            return true;
        }
        return false;
    }
    
    std::string SanitizeFilename(const std::string& filename) {
        std::string sanitized = filename;
        std::string invalidChars = "<>:\"|?*\\/";
        for (char& c : sanitized) {
            if (invalidChars.find(c) != std::string::npos || c < 32) {
                c = '_';
            }
        }
        return sanitized;
    }
    
    std::filesystem::path GetTempAvatarPath(const std::string& idString) {
        return GetTempDirectory() / RLProfilePicturesConstants::TEMP_AVATAR_PREFIX / (idString + ".png");
    }
    
    std::filesystem::path GetTempLocalAvatarPath(const std::string& idString) {
        return GetTempDirectory() / RLProfilePicturesConstants::TEMP_LOCAL_PREFIX / (idString + ".png");
    }
    
    std::filesystem::path GetBrightenedLocalAvatarPath() {
        return GetTempDirectory() / RLProfilePicturesConstants::TEMP_LOCAL_AVATAR;
    }
    std::filesystem::path GetTempDirectory() {
        return std::filesystem::path(RLProfilePicturesConstants::TEMP_DIRECTORY);
    }
}
