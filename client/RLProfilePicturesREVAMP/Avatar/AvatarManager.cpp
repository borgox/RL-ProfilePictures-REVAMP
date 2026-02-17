#include "pch.h"
#include "AvatarManager.h"
#include "ImageProcessor.h"
#include "../Config/Constants.h"
#include "../Utils/Logger.h"
#include "../Utils/FileUtils.h"
#include "../Utils/StringUtils.h"
#include "../RocketLeague/RLObjects.h"
#include <fstream>
#include <future>
#include <thread>
#include <iostream>

// =============================================================================
// AVATAR MANAGER IMPLEMENTATION
// Good luck to anyone reading this, may god help you :D
// =============================================================================

AvatarManager::AvatarManager(std::shared_ptr<GameWrapper> gw) : gameWrapper(gw) {
    // Create downloader with callback to LoadAvatar
    downloader = std::make_unique<AvatarDownloader>(gw,
        [this](FUniqueNetId id, const std::vector<uint8_t>& data) {
            this->LoadAvatar(id, data);
        });
}

AvatarManager::~AvatarManager() {
    ClearCache();
}

std::shared_ptr<bool> AvatarManager::GetBrightnessEnabled() {
    extern std::shared_ptr<CVarManagerWrapper> _globalCvarManager;
    if (!_globalCvarManager) {
        RLProfilePicturesLogger::LogDebug("CVarManager not available");
        return nullptr;
    }

    CVarWrapper brightnessCvar = _globalCvarManager->getCvar(RLProfilePicturesConstants::CVAR_BRIGHTNESS_ADJUSTMENT_ENABLED);
    if (!brightnessCvar) {
        RLProfilePicturesLogger::LogDebug("Brightness adjustment CVar not found");
        return nullptr;
    }

    return std::make_shared<bool>(brightnessCvar.getBoolValue());
}

void AvatarManager::AddLocalAvatar(const std::filesystem::path& filePath) {
    APlayerControllerBase_TA* pc = RL::GetPlayerController();
    UVanitySetManager_TA* vman = RL::GetVanitySetManager();
    if (!pc || !vman) {
        RLProfilePicturesLogger::LogDebug("AddLocalAvatar: PlayerController or VanityManager missing");
        return;
    }

    FUniqueNetId uniqueId = RL::GetPrimaryPlayerID() ? *RL::GetPrimaryPlayerID() : FUniqueNetId{};
    if (!uniqueId.Uid && uniqueId.EpicAccountId.ToString().empty()) {
        RLProfilePicturesLogger::LogDebug("AddLocalAvatar: Invalid UniqueID");
        return;
    }

    std::string filePathString = RLProfilePicturesFileUtils::WStringToUtf8(filePath.c_str()); // .string() crashes if file path contains unicode characters on Windows, soo it's safer to first get it into native and then convert.

    try {
        // Read original file
        std::ifstream file(filePath, std::ios::binary);
        if (!file.good()) {
            RLProfilePicturesLogger::LogError("Cannot read file: " + filePathString);
            return;
        }
        std::vector<uint8_t> originalData((std::istreambuf_iterator<char>(file)),
            std::istreambuf_iterator<char>());
        file.close();

        // Process
        auto brightnessEnabled = GetBrightnessEnabled();
        std::vector<uint8_t> processedData =
            RLProfilePicturesImageProcessor::BrightenImage(originalData, brightnessEnabled);

        // Apply avatar within gameWrapper context (no cache clearing or removal to prevent flickering)
        gameWrapper->Execute([this, uniqueId, processedData, filePath](GameWrapper* gw) {
            try {
                // Get ID string in proper context
                std::string idString = RLProfilePicturesStringUtils::SanitizeFilename(
                    UOnline_X::UniqueNetIdToString(uniqueId).ToString());

                // For Epic platform: Upload to CDN, then load locally
                if (static_cast<EOnlinePlatform>(uniqueId.Platform) == EOnlinePlatform::OnlinePlatform_Epic) {
                    RLProfilePicturesLogger::LogInfo("Uploading processed avatar to CDN...");

                    // Save processed data to temp file for upload
                    std::filesystem::path tempPath = RLProfilePicturesFileUtils::GetBrightenedLocalAvatarPath();
                    std::string temoPathString = RLProfilePicturesFileUtils::WStringToUtf8(tempPath.c_str()); // .string() crashes if file path contains unicode characters on Windows, soo it's safer to first get it into native and then convert.

                    {
                        std::ofstream tempFile(tempPath, std::ios::binary);
                        if (!tempFile.good()) {
                            RLProfilePicturesLogger::LogError("Cannot create temp file: " + temoPathString);
                            return;
                        }
                        tempFile.write(reinterpret_cast<const char*>(processedData.data()), processedData.size());
                    }

                    // Copy data to shared_ptr for safe lambda capture
                    auto dataCopy = std::make_shared<std::vector<uint8_t>>(processedData);

                    // Upload to CDN, then apply locally (using already-processed data)
                    downloader->UploadToCDN(
                        tempPath,
                        uniqueId.EpicAccountId.ToString(),
                        [this, uniqueId, dataCopy, tempPath](bool success) {
                            if (success) {
                                RLProfilePicturesLogger::LogInfo("Upload complete -> applying local processed image");
                            }
                            else {
                                RLProfilePicturesLogger::LogError("Upload failed, but applying local image anyway");
                            }

                            // Apply within gameWrapper context
                            gameWrapper->Execute([this, uniqueId, dataCopy](GameWrapper* gw) {
                                std::string idStr = RLProfilePicturesStringUtils::SanitizeFilename(
                                    UOnline_X::UniqueNetIdToString(uniqueId).ToString());
                                LoadAvatarDirect(uniqueId, idStr, *dataCopy, true);
                                });

                            // Clean up temp file
                            std::filesystem::remove(tempPath);
                        });
                }
                else {
                    // Non-Epic -> directly feed processed bytes
                    RLProfilePicturesLogger::LogDebug("Non-Epic platform: applying processed avatar locally");
                    LoadAvatarDirect(uniqueId, idString, processedData, true);
                }
            }
            catch (const std::exception& e) {
                RLProfilePicturesLogger::LogError("Exception in AddLocalAvatar Execute: " + std::string(e.what()));
            }
            });
    }
    catch (const std::exception& e) {
        RLProfilePicturesLogger::LogError("Exception in AddLocalAvatar: " + std::string(e.what()));
    }
}

// Load avatar without re-applying brightness (already processed data)
void AvatarManager::LoadAvatarDirect(FUniqueNetId id, const std::string& idString, const std::vector<uint8_t>& alreadyProcessedData, bool forceUpdate) {
    RLProfilePicturesLogger::LogDebug("LoadAvatarDirect called for ID: " + idString +
        " with data size: " + std::to_string(alreadyProcessedData.size()) + 
        ", forceUpdate: " + (forceUpdate ? "true" : "false"));

    // Check cache first (unless forcing update)
    UTexture2DDynamic* tex = nullptr;
    if (!forceUpdate) {
        auto it = avatar_cache.find(idString);
        if (it != avatar_cache.end() && it->second) {
            tex = it->second;
            RLProfilePicturesLogger::LogDebug("Avatar found in cache for ID: " + idString);
            SetAvatar(id, tex);
            return;
        }
    }

    try {
        std::filesystem::path filePath = RLProfilePicturesFileUtils::GetTempAvatarPath(idString);
        std::string filePathString = RLProfilePicturesFileUtils::WStringToUtf8(filePath.c_str()); // .string() crashes if file path contains unicode characters on Windows, soo it's safer to first get it into native and then convert.

        RLProfilePicturesLogger::LogDebug("Attempting to write avatar file: " + filePathString); 


        {

            std::ofstream out(filePath, std::ios::binary);
            if (!out) {
                RLProfilePicturesLogger::LogDebug("Failed to open file for writing: " + filePathString);
                return;
            }
            out.write(reinterpret_cast<const char*>(alreadyProcessedData.data()), alreadyProcessedData.size());
            out.flush();
            if (!out.good()) {
                RLProfilePicturesLogger::LogDebug("Failed to write data to file: " + filePathString);
                return;
            }
            RLProfilePicturesLogger::LogDebug("Successfully wrote " + std::to_string(alreadyProcessedData.size()) +
                " bytes to: " + filePathString);
        }

        // Verify file was created
        std::ifstream fileCheck(filePath);
        if (!fileCheck.good()) {
            RLProfilePicturesLogger::LogDebug("File does not exist after writing: " + filePathString);
            return;
        }
        fileCheck.close();

        auto img = std::make_unique<ImageWrapper>(filePath, true, false);
        if (!img->LoadForCanvas()) {
            RLProfilePicturesLogger::LogDebug("Failed to load image from file: " + filePathString);
            std::filesystem::remove(filePath);
            return;
        }

        // Clean up temporary file
        std::filesystem::remove(filePath);

        tex = static_cast<UTexture2DDynamic*>(img->GetCanvasTex());
        if (!tex) {
            RLProfilePicturesLogger::LogDebug("Failed to get texture from image: " + filePathString);
            return;
        }

        // Cache the texture
        avatar_cache[idString] = tex;
        SetAvatar(id, tex);
        RLProfilePicturesLogger::LogSuccess("Avatar loaded successfully for ID: " + idString);
    }
    catch (const std::exception& e) {
        RLProfilePicturesLogger::LogError("Exception in LoadAvatarDirect: " + std::string(e.what()));
    }
}


void AvatarManager::RemoveLocalAvatar() {
    APlayerControllerBase_TA* pc = RL::GetPlayerController();
    UVanitySetManager_TA* vman = RL::GetVanitySetManager();
    if (!pc || !vman) return;

    FUniqueNetId uniqueId = RL::GetPrimaryPlayerID() ? *RL::GetPrimaryPlayerID() : FUniqueNetId{};
    if (!uniqueId.Uid && uniqueId.EpicAccountId.ToString().empty()) return;

    UPlayerAvatar_TA* avatar = vman->GetAvatar(uniqueId);
    if (!avatar) {
        RLProfilePicturesLogger::LogError("No avatar component found to remove!");
        return;
    }

    pc->PlayerAvatar = nullptr;
    avatar->HandleUpdateTexture(nullptr);
    vman->HandleLoadedAvatarAsset(avatar);
	// Clear cache entry
	std::string idString = UOnline_X::UniqueNetIdToString(uniqueId).ToString();
	avatar_cache.erase(idString);
    for (const auto& [key, tex] : avatar_cache) {
        RLProfilePicturesLogger::LogDebug("Cache entry remains: " + key);
    }
    RLProfilePicturesLogger::LogSuccess("Avatar removed successfully");
}

void AvatarManager::LoadAvatar(FUniqueNetId id, const std::vector<uint8_t>& data) {
    std::string idString = RLProfilePicturesStringUtils::SanitizeFilename(
        UOnline_X::UniqueNetIdToString(id).ToString());
    RLProfilePicturesLogger::LogDebug("LoadAvatar called for ID: " + idString +
        " with data size: " + std::to_string(data.size()));

    // Check cache first
    UTexture2DDynamic* tex = nullptr;
    auto it = avatar_cache.find(idString);
    if (it != avatar_cache.end() && it->second) {
        tex = it->second;
        RLProfilePicturesLogger::LogDebug("Avatar found in cache for ID: " + idString);
        SetAvatar(id, tex);
        return;
    }

    try {
        // Apply brightness adjustment before processing
        auto brightnessEnabled = GetBrightnessEnabled();
        std::vector<uint8_t> brightenedData = RLProfilePicturesImageProcessor::BrightenImage(data, brightnessEnabled);

        std::filesystem::path filePath = RLProfilePicturesFileUtils::GetTempAvatarPath(idString);
        std::string filePathString = RLProfilePicturesFileUtils::WStringToUtf8(filePath.c_str()); // .string() crashes if file path contains unicode characters on Windows, soo it's safer to first get it into native and then convert.

        RLProfilePicturesLogger::LogDebug("Attempting to write brightened avatar file: " + filePathString);


        {
            std::ofstream out(filePath, std::ios::binary);
            if (!out) {
                RLProfilePicturesLogger::LogDebug("Failed to open file for writing: " + filePathString);
                return;
            }
            out.write(reinterpret_cast<const char*>(brightenedData.data()), brightenedData.size());
            out.flush();
            if (!out.good()) {
                RLProfilePicturesLogger::LogDebug("Failed to write data to file: " + filePathString);
                return;
            }
            RLProfilePicturesLogger::LogDebug("Successfully wrote " + std::to_string(brightenedData.size()) +
                " bytes to: " + filePathString);
        }

        // Verify file was created
        std::ifstream fileCheck(filePath);
        if (!fileCheck.good()) {
            RLProfilePicturesLogger::LogDebug("File does not exist after writing: " + filePathString);
            return;
        }
        fileCheck.close();

        auto img = std::make_unique<ImageWrapper>(filePath, true, false);
        if (!img->LoadForCanvas()) {
            RLProfilePicturesLogger::LogDebug("Failed to load image from file: " + filePathString);
            std::filesystem::remove(filePath);
            return;
        }

        // Clean up temporary file
        std::filesystem::remove(filePath);

        tex = static_cast<UTexture2DDynamic*>(img->GetCanvasTex());
        if (!tex) {
            RLProfilePicturesLogger::LogDebug("Failed to get texture from image: " + filePathString);
            return;
        }

        // Cache the texture
        avatar_cache[idString] = tex;
        SetAvatar(id, tex);
    }
    catch (const std::exception& e) {
        RLProfilePicturesLogger::LogError("Exception in LoadAvatar: " + std::string(e.what()));
    }
}

void AvatarManager::SetAvatar(FUniqueNetId id, UTexture2DDynamic* tex) {
    std::string idString = UOnline_X::UniqueNetIdToString(id).ToString();
    RLProfilePicturesLogger::LogDebug("SetAvatar called for ID: " + idString);
    UObject* pcObj = reinterpret_cast <UObject*> (gameWrapper->GetPlayerController().memory_address);
    if (!pcObj) {
        RLProfilePicturesLogger::LogError("SetAvatar: gameWrapper->GetPlayerController() returned null");
        return;
    }
    if (!tex) {
        RLProfilePicturesLogger::LogError("SetAvatar: No texture provided to set!");
        return;
	}
    APlayerController_TA* pc = Cast < APlayerController_TA >(pcObj);
    if (!pc) {
        RLProfilePicturesLogger::LogError("SetAvatar: PlayerController cast failed, assuming local player");
        APlayerControllerBase_TA* pc = RL::GetPlayerController();
        UVanitySetManager_TA* vman = RL::GetVanitySetManager();
        if (!pc || !vman) {
            RLProfilePicturesLogger::LogDebug("AddLocalAvatar: PlayerController or VanityManager missing");
            return;
        }
        UPlayerAvatar_TA* avatar = vman->GetAvatar(id);
        if (!avatar) {
            RLProfilePicturesLogger::LogError("No avatar component found!");
            return;
        }
        if (!tex) {
            RLProfilePicturesLogger::LogError("No texture provided to set!");
            return;
		}
        pc->PlayerAvatar = avatar;
        avatar->HandleUpdateTexture(tex);
        vman->HandleLoadedAvatarAsset(avatar);
        UGFxShell_X* shell = RL::GetShell();
        if (!shell) {
            RLProfilePicturesLogger::LogDebug("AddLocalAvatar: GFxShell_X missing");
            return;
        }
        UGFxData_PlayerAvatar_TA* avatarData = UGFxData_PlayerAvatar_TA::GetOrCreate(shell, avatar);
        if (!avatarData) {
            RLProfilePicturesLogger::LogDebug("AddLocalAvatar: UGFxData_PlayerAvatar_TA missing");
            return;
        }
        UGFxDataStore_X* dataStore = shell->DataStore;
        if (!dataStore) {
            RLProfilePicturesLogger::LogDebug("AddLocalAvatar: DataStore missing");
            return;
        }
        dataStore->SetTextureValue(avatarData->TableName, avatarData->RowIndex, L"ToPlayer", tex);
        RLProfilePicturesLogger::LogSuccess("SetAvatar: Avatar set successfully for local player");
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Got PlayerController");
    if (!pc->PRI) {
        RLProfilePicturesLogger::LogError("SetAvatar: PlayerController->PRI is null");
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Got PlayerController->PRI");
    AGameEvent_TA* event = pc->PRI->GameEvent;
    if (!event) {
        RLProfilePicturesLogger::LogError("SetAvatar: GameEvent is null");
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Got GameEvent");
    APRI_TA* pri = event->FindPlayerPRI(id);
    if (!pri) {
        RLProfilePicturesLogger::LogError("SetAvatar: Failed to find PRI for ID: " + idString);
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Found PRI for " + pri->PlayerName.ToString());
    if (pri->IsLocalPlayerPRI()) {
        RLProfilePicturesLogger::LogDebug("SetAvatar: Local PRI, using random ahh stuff");
        UVanitySetManager_TA* vman = RL::GetVanitySetManager();
        if (!pc || !vman) {
            RLProfilePicturesLogger::LogDebug("AddLocalAvatar: PlayerController or VanityManager missing");
            return;
        }
        UPlayerAvatar_TA* avatar = vman->GetAvatar(id);
        if (!avatar) {
            RLProfilePicturesLogger::LogError("No avatar component found!");
            return;
        }
        if (!tex) {
            RLProfilePicturesLogger::LogError("No texture provided to set!");
            return;
        }
        pc->PlayerAvatar = avatar;
        avatar->HandleUpdateTexture(tex);
        vman->HandleLoadedAvatarAsset(avatar);
        UGFxShell_X* shell = RL::GetShell();
        if (!shell) {
            RLProfilePicturesLogger::LogDebug("AddLocalAvatar: GFxShell_X missing");
            return;
        }
        UGFxData_PlayerAvatar_TA* avatarData = UGFxData_PlayerAvatar_TA::GetOrCreate(shell, avatar);
        if (!avatarData) {
            RLProfilePicturesLogger::LogDebug("AddLocalAvatar: UGFxData_PlayerAvatar_TA missing");
            return;
        }
        UGFxDataStore_X* dataStore = shell->DataStore;
        if (!dataStore) {
            RLProfilePicturesLogger::LogDebug("AddLocalAvatar: DataStore missing");
            return;
        }
        dataStore->SetTextureValue(avatarData->TableName, avatarData->RowIndex, L"ToPlayer", tex);
        RLProfilePicturesLogger::LogSuccess("SetAvatar: Avatar set successfully for local player");
        return;
        return;
    }
    UVanitySetManager_TA* vanitySet = pc->VanityMgr;
    if (!vanitySet) {
        RLProfilePicturesLogger::LogError("SetAvatar: VanitySetManager is null");
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Got VanitySetManager");
    UPlayerAvatar_TA* avatar = vanitySet->GetAvatar(id);
    if (!avatar) {
        RLProfilePicturesLogger::LogError("SetAvatar: No avatar found in VanitySetManager for ID: " + idString);
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Got UPlayerAvatar_TA");
    UGFxShell_TA* shell = RL::GetShell();
    if (!shell) {
        RLProfilePicturesLogger::LogError("SetAvatar: GFxShell is null");
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Got GFxShell");
    UGFxData_PlayerAvatar_TA* avatarData = UGFxData_PlayerAvatar_TA::GetOrCreate(shell, avatar);
    if (!avatarData) {
        RLProfilePicturesLogger::LogError("SetAvatar: Failed to get or create UGFxData_PlayerAvatar_TA");
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Got UGFxData_PlayerAvatar_TA");
    UGFxDataStore_X* dataStore = shell->DataStore;
    if (!dataStore) {
        RLProfilePicturesLogger::LogError("SetAvatar: DataStore is null");
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Got DataStore");
    dataStore->SetTextureValue(avatarData->TableName, avatarData->RowIndex, L"ToPlayer", tex);
    RLProfilePicturesLogger::LogDebug("SetAvatar: SetTextureValue called");
    pc->PlayerAvatar = avatar;
    avatar->HandleUpdateTexture(tex);
    vanitySet->HandleLoadedAvatarAsset(avatar);
    RLProfilePicturesLogger::LogDebug("SetAvatar: Avatar texture applied");
    AGFxHUD_TA* hud = Cast < AGFxHUD_TA >(pc->myHUD);
    if (!hud) {
        RLProfilePicturesLogger::LogError("SetAvatar: HUD is null");
        return;
    }
    RLProfilePicturesLogger::LogDebug("SetAvatar: Got HUD");
    UGFxData_PRI_TA* priData = hud->GetPRIDataFromID(id);
    if (priData) {
        RLProfilePicturesLogger::LogDebug("SetAvatar: Updating PRIData for " + pri->PlayerName.ToString());
        priData->UpdatePRIData();
    }
    else {
        RLProfilePicturesLogger::LogError("SetAvatar: Failed to get PRIData from HUD");
    }
    RLProfilePicturesLogger::LogSuccess("SetAvatar: Avatar set successfully for player: " + pri->PlayerName.ToString());
}
void AvatarManager::ApplyAvatar(UPlayerAvatar_TA* avatar, UTexture2DDynamic* tex) {
    if (!avatar) {
        RLProfilePicturesLogger::LogError("ApplyAvatar: avatar is null");
        return;
    }

    UGFxShell_X* shell = RL::GetShell();
    if (!shell) {
        RLProfilePicturesLogger::LogError("ApplyAvatar: GFxShell_X missing");
        return;
    }

    UGFxData_PlayerAvatar_TA* avatarData = UGFxData_PlayerAvatar_TA::GetOrCreate(shell, avatar);
    if (!avatarData) {
        RLProfilePicturesLogger::LogError("ApplyAvatar: Failed to get or create UGFxData_PlayerAvatar_TA");
        return;
    }

    UGFxDataStore_X* dataStore = shell->DataStore;
    if (!dataStore) {
        RLProfilePicturesLogger::LogError("ApplyAvatar: DataStore missing");
        return;
    }

    dataStore->SetTextureValue(avatarData->TableName, avatarData->RowIndex, L"ToPlayer", tex);

    avatar->HandleUpdateTexture(tex);

    RLProfilePicturesLogger::LogDebug("ApplyAvatar: Avatar texture updated successfully");
}

void AvatarManager::RemoveUserAvatar(FUniqueNetId id) {
    UObject* pcObj = reinterpret_cast<UObject*>(gameWrapper->GetPlayerController().memory_address);
    APlayerController_TA* pc = Cast<APlayerController_TA>(pcObj);
    std::string idString = UOnline_X::UniqueNetIdToString(id).ToString();
    AGameEvent_TA* event = pc->PRI->GameEvent;
    if (!event) return;
    APRI_TA* pri = event->FindPlayerPRI(id);
    if (!pri) return;

    UVanitySetManager_TA* vanitySet = pc->VanityMgr;
    UPlayerAvatar_TA* avatar = vanitySet->GetAvatar(id);
	if (!vanitySet) return;
    if (!avatar) return;

    UGFxData_PlayerAvatar_TA* avatarData = UGFxData_PlayerAvatar_TA::GetOrCreate(RL::GetShell(), avatar);
    UGFxDataStore_X* dataStore = RL::GetShell()->DataStore;

    if (!dataStore) return;
    dataStore->SetTextureValue(avatarData->TableName, avatarData->RowIndex, L"ToPlayer", nullptr);

    pri->PlayerAvatar = nullptr;
    avatar->HandleUpdateTexture(nullptr);
    vanitySet->HandleLoadedAvatarAsset(avatar);

    AGFxHUD_TA* hud = Cast<AGFxHUD_TA>(pc->myHUD);
    if (!hud) return;

    UGFxData_PRI_TA* priData = hud->GetPRIDataFromID(id);
    if (priData) {
        priData->UpdatePRIData();
    }

    RLProfilePicturesLogger::LogSuccess("Avatar removed for player: " + pri->PlayerName.ToString());
}

void AvatarManager::LoadForPRI(APRI_TA* pri) {
    UObject* pcObj = reinterpret_cast<UObject*>(gameWrapper->GetPlayerController().memory_address);
    APlayerController_TA* pc = Cast<APlayerController_TA>(pcObj);
    if (!pc || !pri) {
        RLProfilePicturesLogger::LogDebug("LoadForPRI: PlayerController or PRI missing");
        return;
    }

    // Compare the local and PRI unique IDs - skip if same player
    FUniqueNetId* localId = pc->PRI ? &pc->PRI->UniqueId : nullptr;
    FUniqueNetId* priId = pri ? &pri->UniqueId : nullptr;

    if (!localId || !priId) {
        RLProfilePicturesLogger::LogDebug("LoadForPRI: LocalID or PRI ID missing");
        return;
    }
    if (localId->Uid == priId->Uid && localId->EpicAccountId.ToString() == priId->EpicAccountId.ToString()) {
        RLProfilePicturesLogger::LogDebug("LoadForPRI: Local player detected, skipping");
        return;
    }

    FUniqueNetId uniqueId = pri->UniqueId;

    // Xbox platform requires special handling with player names
    if (static_cast<EOnlinePlatform>(uniqueId.Platform) == EOnlinePlatform::OnlinePlatform_Dingo) {
        std::string playername = pri->PlayerName.ToString();
        auto future = std::async(std::launch::async, [this, uniqueId, playername]() {
            this->downloader->DownloadXboxAvatar(uniqueId, playername);
            });
        return;
    }

    // Check if avatar is already cached
    std::string idString = UOnline_X::UniqueNetIdToString(uniqueId).ToString();
    UTexture2DDynamic* tex = GetCachedAvatar(idString);
    if (tex) {
        RLProfilePicturesLogger::LogDebug("Using cached avatar for ID: " + idString);
        SetAvatar(uniqueId, tex);
    }
    else {
        RLProfilePicturesLogger::LogDebug("Downloading avatar for ID: " + idString);
        auto future = std::async(std::launch::async, [this, uniqueId]() {
            this->downloader->DownloadAvatar(uniqueId);
            });
    }
}

void AvatarManager::ClearCache() {
    avatar_cache.clear();
    RLProfilePicturesLogger::LogDebug("Avatar cache cleared");
}

bool AvatarManager::IsAvatarCached(const std::string& idString) {
    auto it = avatar_cache.find(idString);
    return (it != avatar_cache.end() && it->second != nullptr);
}

UTexture2DDynamic* AvatarManager::GetCachedAvatar(const std::string& idString) {
    auto it = avatar_cache.find(idString);
    return (it != avatar_cache.end()) ? it->second : nullptr;
}
