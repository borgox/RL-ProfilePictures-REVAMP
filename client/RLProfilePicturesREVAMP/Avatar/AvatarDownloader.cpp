#include "pch.h"
#include "AvatarDownloader.h"
#include "../Config/Constants.h"
#include "../Utils/Logger.h"
#include "../Utils/FileUtils.h"
#include "../RocketLeague/RLObjects.h"
#include <format>

// Forward declaration for AvatarManager
class AvatarManager;

// =============================================================================
// AVATAR DOWNLOADER
// =============================================================================

AvatarDownloader::AvatarDownloader(std::shared_ptr<GameWrapper> gw, 
                                   std::function<void(FUniqueNetId, const std::vector<uint8_t>&)> callback) 
    : gameWrapper(gw), loadAvatarCallback(callback) {}

std::string AvatarDownloader::GetURLForID(FUniqueNetId id) {
    if (!IsAllowed(id))
        return "";
    
    std::string baseUrl = RLProfilePicturesConstants::API_BASE_URL;
	// Know if the default avatar should be returned if none is set
	// Get from CVar, default to true if CVarManager not available
	bool default_value = _globalCvarManager->getCvar(RLProfilePicturesConstants::CVAR_LOAD_DEFAULT_AVATARS).getBoolValue();
	std::string default_enabled = default_value ? "true" : "false";
    switch (static_cast<EOnlinePlatform>(id.Platform)) {
    case EOnlinePlatform::OnlinePlatform_Steam:
        return baseUrl + RLProfilePicturesConstants::API_STEAM_RETRIEVE + std::to_string(id.Uid) + "?default_enabled=" + default_enabled;
    case EOnlinePlatform::OnlinePlatform_Epic:
        return baseUrl + RLProfilePicturesConstants::API_EPIC_RETRIEVE + id.EpicAccountId.ToString() + "?default_enabled=" + default_enabled;
    case EOnlinePlatform::OnlinePlatform_Dingo: // Xbox
        return ""; // Xbox uses DownloadXboxAvatar with player names
    case EOnlinePlatform::OnlinePlatform_PS4:
        return baseUrl + RLProfilePicturesConstants::API_PSN_RETRIEVE + std::to_string(id.Uid) + "?default_enabled=" + default_enabled;
    case EOnlinePlatform::OnlinePlatform_NNX: // Switch
        return baseUrl + RLProfilePicturesConstants::API_SWITCH_RETRIEVE + std::to_string(id.Uid) + "?default_enabled=" + default_enabled;
    }
    return "";
}

bool AvatarDownloader::IsAllowed(FUniqueNetId id) {
    // Check if local player is on Steam (affects Steam avatar policy)
    bool localOnSteam = false;
    if (auto* localId = RL::GetPrimaryPlayerID()) {
        localOnSteam = (static_cast<EOnlinePlatform>(localId->Platform) == EOnlinePlatform::OnlinePlatform_Steam);
    }
    
    // Helper lambda to get CVar values safely
    auto getCVarBool = [](const char* name) -> bool {
        extern std::shared_ptr<CVarManagerWrapper> _globalCvarManager;
        if (!_globalCvarManager) return false;
        CVarWrapper cv = _globalCvarManager->getCvar(name);
        return !cv.IsNull() && cv.getBoolValue();
    };
    
    switch (static_cast<EOnlinePlatform>(id.Platform)) {
    case EOnlinePlatform::OnlinePlatform_Steam:
        // Only allow Steam avatars if local player is NOT on Steam (game handles local Steam avatars)
        return !localOnSteam && getCVarBool(RLProfilePicturesConstants::CVAR_STEAM_ENABLED);
        
    case EOnlinePlatform::OnlinePlatform_Epic:
        return getCVarBool(RLProfilePicturesConstants::CVAR_EPIC_ENABLED);
        
    case EOnlinePlatform::OnlinePlatform_Dingo: // Xbox
        return getCVarBool(RLProfilePicturesConstants::CVAR_XBOX_ENABLED);
        
    case EOnlinePlatform::OnlinePlatform_PS4:
        return getCVarBool(RLProfilePicturesConstants::CVAR_PSN_ENABLED);
        
    case EOnlinePlatform::OnlinePlatform_NNX: // Switch
        return getCVarBool(RLProfilePicturesConstants::CVAR_SWITCH_ENABLED);
        
    default:
        return false;
    }
}

void AvatarDownloader::DownloadAvatar(FUniqueNetId id) {
    std::string idString = UOnline_X::UniqueNetIdToString(id).ToString();
    std::string url = GetURLForID(id);
    
    RLProfilePicturesLogger::LogDebug("DownloadAvatar called for ID: " + idString);
    
    if (url.empty()) {
        RLProfilePicturesLogger::LogDebug("Empty URL for ID: " + idString);
        return;
    }
    
    // TODO: Check avatar cache here (will be implemented in AvatarManager) 
    // a fucking TODO that existed from before dinosaurs existed, now i dont even know what it meant
    
    CurlRequest req;
    req.url = url;
    req.verb = "GET";
    
    HttpWrapper::SendCurlRequest(req, [this, id, idString](int http_code, char* data_ptr, size_t data_size) {
        RLProfilePicturesLogger::LogDebug("HTTP response for ID " + idString + ": code=" + 
                                         std::to_string(http_code) + ", size=" + std::to_string(data_size));
        
        if (http_code != 200) {
            RLProfilePicturesLogger::LogDebug("HTTP request failed for ID " + idString + 
                                             " with code: " + std::to_string(http_code));
            return;
        }
        
        if (data_ptr == nullptr || data_size == 0) {
            RLProfilePicturesLogger::LogDebug("No data received for ID: " + idString);
            
            return;
        }
        
        std::vector<uint8_t> data(data_ptr, data_ptr + data_size);
        
        // Use gameWrapper->Execute to ensure we're on the game thread
        gameWrapper->Execute([this, id, data](GameWrapper* gw) {
            RLProfilePicturesLogger::LogSuccess("Avatar downloaded for ID: " + 
                                               UOnline_X::UniqueNetIdToString(id).ToString());
            if (loadAvatarCallback) {
                loadAvatarCallback(id, data);
            }
        });
    });
}

void AvatarDownloader::DownloadXboxAvatar(FUniqueNetId id, std::string playername) {
    bool default_value = _globalCvarManager->getCvar(RLProfilePicturesConstants::CVAR_LOAD_DEFAULT_AVATARS).getBoolValue();
    std::string default_enabled = default_value ? "true" : "false";
    std::string url = std::string(RLProfilePicturesConstants::API_BASE_URL) + 
                     RLProfilePicturesConstants::API_XBOX_RETRIEVE + playername + "?default_enabled=" + default_enabled;
    std::string idString = UOnline_X::UniqueNetIdToString(id).ToString();
    
    // TODO: Check avatar cache here (will be implemented in AvatarManager)
    
    CurlRequest req;
    req.url = url;
    req.verb = "GET";
    
    HttpWrapper::SendCurlRequest(req, [this, id, idString](int http_code, char* data_ptr, size_t data_size) {
        RLProfilePicturesLogger::LogDebug("HTTP response for ID " + idString + ": code=" + 
                                         std::to_string(http_code) + ", size=" + std::to_string(data_size));
        
        if (http_code != 200) {
            RLProfilePicturesLogger::LogDebug("HTTP request failed for ID " + idString + 
                                             " with code: " + std::to_string(http_code));
            return;
        }
        
        if (data_ptr == nullptr || data_size == 0) {
            RLProfilePicturesLogger::LogDebug("No data received for ID: " + idString);
            return;
        }
        
        std::vector<uint8_t> data(data_ptr, data_ptr + data_size);
        
        // Use gameWrapper->Execute to ensure we're on the game thread
        gameWrapper->Execute([this, id, data](GameWrapper* gw) {
            RLProfilePicturesLogger::LogSuccess("Avatar downloaded for ID: " + 
                                               UOnline_X::UniqueNetIdToString(id).ToString());
            if (loadAvatarCallback) {
                loadAvatarCallback(id, data);
            }
        });
    });
}

void AvatarDownloader::UploadToCDN(const std::filesystem::path& filePath,
    const std::string& epic_id,
    std::function<void(bool)> callback) {
    if (filePath.empty() || epic_id.empty()) {
        RLProfilePicturesLogger::LogError("File path or Epic ID is empty, cannot upload avatar.");
        if (callback) callback(false);
        return;
    }

    std::string filePathString = RLProfilePicturesFileUtils::WStringToUtf8(filePath.c_str()); // .string() crashes if file path contains unicode characters on Windows, soo it's safer to first get it into native and then convert.

    CurlRequest req;
    req.url = std::string(RLProfilePicturesConstants::API_BASE_URL) +
        RLProfilePicturesConstants::API_EPIC_UPLOAD + epic_id;
    req.verb = "POST";
    req.headers["accept"] = "application/json";

    FormField fileField;
    fileField.field_type = FormField::Type::kFile;
    fileField.name = "file";
    fileField.data = filePathString;
    req.form_data.push_back(fileField);

    HttpWrapper::SendCurlRequest(req, [epic_id, filePath, callback](int http_code, std::string data) {
        bool success = false;

        if (!data.empty() && http_code == 200) {
            if (data.find("\"success\":true") != std::string::npos ||
                (data.find("success") != std::string::npos && data.find("true") != std::string::npos)) {
                success = true;
                RLProfilePicturesLogger::LogSuccess("Avatar uploaded successfully for Epic ID: " + epic_id);
            }
            else {
                RLProfilePicturesLogger::LogError("CDN upload failed. Response: " + data);
            }
        }
        else {
            RLProfilePicturesLogger::LogError("Failed to upload. HTTP: " + std::to_string(http_code));
        }

        std::filesystem::remove(filePath);
        if (callback) callback(success);
    });
}
