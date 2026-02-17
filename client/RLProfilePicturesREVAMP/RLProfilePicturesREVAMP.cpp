#include "pch.h"
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#include "RLProfilePicturesREVAMP.h"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <future>
#include <thread>
#include <filesystem>

BAKKESMOD_PLUGIN(RLProfilePicturesREVAMP, "RLProfilePicturesREVAMP", plugin_version, PLUGINTYPE_FREEPLAY)

// Global CVarManager for access from other modules
std::shared_ptr<CVarManagerWrapper> _globalCvarManager;

// GObjects and GNames are defined in RLSDK/GameDefines.cpp and declared extern in GameDefines.hpp

// =============================================================================
// PLUGIN IMPLEMENTATION
// =============================================================================

void RLProfilePicturesREVAMP::onLoad() {
    _globalCvarManager = cvarManager;
    
    // Initialize memory scanning
    {
        MemoryHelper rl;
        const uintptr_t gnamesAddress = rl.FindPattern(RLProfilePicturesConstants::GNAMES_PATTERN);
        const uintptr_t gobjectsAddress = gnamesAddress + RLProfilePicturesConstants::GOBJ_OFFSET;
        GNames = reinterpret_cast<TArray<FNameEntry*>*>(gnamesAddress);
        GObjects = reinterpret_cast<TArray<UObject*>*>(gobjectsAddress);
    }
    
    // Initialize plugin components
    InitializeCVars();
    InitializeModules();
    RegisterEventHooks();
    
    // Ensure temp directory exists
    if (!RLProfilePicturesFileUtils::EnsureTempDirectoryExists()) {
        RLProfilePicturesLogger::LogError("Failed to create temp directory");
    }
    
    RLProfilePicturesLogger::LogInfo("RLProfilePicturesREVAMP loaded!");
    
    // Load avatar on startup if applicable
    LoadStartupAvatar();
}

void RLProfilePicturesREVAMP::InitializeModules() {
    // Initialize logger
    RLProfilePicturesLogger::Initialize(cvarManager, debug_logs);
    
    // Initialize avatar manager
    avatarManager = std::make_shared<AvatarManager>(gameWrapper);
    
    // Initialize settings UI
    settingsUI = std::make_unique<SettingsUI>(gameWrapper, avatarManager);
}

void RLProfilePicturesREVAMP::InitializeCVars() {
    // Main plugin settings
    CVarWrapper cvarEnabled = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_ENABLED, "1",
        "Enable the RLProfilePicturesREVAMP plugin", true, true, 0, true, 1);
    cvarEnabled.bindTo(enabled);
    *enabled = cvarEnabled.getBoolValue();

    CVarWrapper cvarDebug = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_DEBUG_LOGS, "1",
        "Enable debug logs", true, true, 0, true, 1);
    cvarDebug.bindTo(debug_logs);
    *debug_logs = cvarDebug.getBoolValue();

    // Platform settings
    CVarWrapper cvarSteam = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_STEAM_ENABLED, "1",
        "Enable Steam profile pictures", true, true, 0, true, 1);
    cvarSteam.bindTo(steam_enabled);
    *steam_enabled = cvarSteam.getBoolValue();

    CVarWrapper cvarEpic = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_EPIC_ENABLED, "1",
        "Enable Epic profile pictures", true, true, 0, true, 1);
    cvarEpic.bindTo(epic_enabled);
    *epic_enabled = cvarEpic.getBoolValue();

    CVarWrapper cvarXbox = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_XBOX_ENABLED, "1",
        "Enable Xbox profile pictures", true, true, 0, true, 1);
    cvarXbox.bindTo(xbox_enabled);
    *xbox_enabled = cvarXbox.getBoolValue();

    CVarWrapper cvarPSN = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_PSN_ENABLED, "1",
        "Enable PSN profile pictures", true, true, 0, true, 1);
    cvarPSN.bindTo(psn_enabled);
    *psn_enabled = cvarPSN.getBoolValue();

    CVarWrapper cvarSwitch = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_SWITCH_ENABLED, "1",
        "Enable Switch profile pictures", true, true, 0, true, 1);
    cvarSwitch.bindTo(switch_enabled);
    *switch_enabled = cvarSwitch.getBoolValue();

    // Avatar path setting
    CVarWrapper avatarCvar = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_AVATAR_PATH, 
        RLProfilePicturesConstants::DEFAULT_AVATAR_PATH,
        "Path to local avatar image", false, false, 0, false, 0, true);
    avatarCvar.bindTo(avatar_path_string);
    *avatar_path_string = avatarCvar.getStringValue();
    *avatar_path = std::filesystem::path(*avatar_path_string);
    avatarCvar.addOnValueChanged([this](std::string, CVarWrapper cvar) {
        *avatar_path = std::filesystem::path(*avatar_path_string);
    });

    // Register version cvar
    CVarWrapper verCvar = cvarManager->registerCvar("RLProfilePicturesREVAMP_Version", plugin_version,
		"Current version of RLProfilePicturesREVAMP", false, true, 0, true, 0, false);
    verCvar.addOnValueChanged([this](std::string, CVarWrapper cvar) {
        if (cvar.getStringValue() != plugin_version) {
            cvar.setValue(plugin_version);
        }
        });
    CVarWrapper brightnessCvar = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_BRIGHTNESS_ADJUSTMENT_ENABLED, "1",
		"Enable brightness adjustment for avatars", true, true, 0, true, 1);

    brightnessCvar.bindTo(brightness_enabled);
	*brightness_enabled = brightnessCvar.getBoolValue();

    CVarWrapper loadDefaultAvatarsCvar = cvarManager->registerCvar(RLProfilePicturesConstants::CVAR_LOAD_DEFAULT_AVATARS, "1",
		"Load default avatars for players without custom avatars", true, true, 0, true, 1);
	loadDefaultAvatarsCvar.bindTo(default_avatars_enabled);
	*default_avatars_enabled = loadDefaultAvatarsCvar.getBoolValue();
}

void RLProfilePicturesREVAMP::RegisterEventHooks() {
    // Main menu avatar loading
    gameWrapper->HookEventWithCaller<ActorWrapper>(
        "Function TAGame.GFxData_MainMenu_TA.OnEnteredMainMenu",
        [this](ActorWrapper caller, void* params, std::string eventName) {
            RLProfilePicturesLogger::LogDebug("OnEnteredMainMenu triggered");
            
            if (!*enabled) return;

            std::string avatarPathFromCvar = cvarManager->getCvar(RLProfilePicturesConstants::CVAR_AVATAR_PATH).getStringValue();
            if (avatarPathFromCvar.empty() || avatarPathFromCvar == RLProfilePicturesConstants::DEFAULT_AVATAR_PATH) {
                RLProfilePicturesLogger::LogError("No avatar image selected from cvar! Trying from cdn");
				LoadStartupAvatar();
                return;
            }

            try {
                RLProfilePicturesLogger::LogDebug("Loading avatar from cvar: " + avatarPathFromCvar);
                avatarManager->AddLocalAvatar(avatarPathFromCvar);
                RLProfilePicturesLogger::LogSuccess("Avatar Loaded");
            }
            catch (...) {
                RLProfilePicturesLogger::LogError("Failed to load texture on main menu!");
            }
        });

    // Player replication events for remote avatars
    gameWrapper->HookEventWithCaller<ActorWrapper>(
        "Function TAGame.PRI_TA.ReplicatedEvent",
        [this](ActorWrapper caller, void* params, std::string eventName) {
            if (!*enabled) return;
            
            APRI_TA* pri = reinterpret_cast<APRI_TA*>(caller.memory_address);
            if (!pri || pri->IsLocalPlayerPRI()) {
                return;
            }

            APRI_TA_eventReplicatedEvent_Params* p = reinterpret_cast<APRI_TA_eventReplicatedEvent_Params*>(params);
            if (!p) {
                return;
            }

            FName name = p->VarName;
            if (name.ToString().empty() || name.ToString() != "PlayerName") {
                return;
            }

            avatarManager->LoadForPRI(pri);
        });
        
    // Player avatar updates
    gameWrapper->HookEventWithCaller<ActorWrapper>(
        "Function TAGame.PRI_TA.UpdatePlayerAvatar",
        [this](ActorWrapper caller, void* params, std::string eventName) {
            if (!*enabled) return;
            
            RLProfilePicturesLogger::LogDebug("UpdatePlayerAvatar called");
            APRI_TA* pri = reinterpret_cast<APRI_TA*>(caller.memory_address);
            if (!pri || pri->IsLocalPlayerPRI()) {
                return;
            }
            avatarManager->LoadForPRI(pri);
        });
        
    //Match start/end events for cache clearing (if CLEAR_AVATARS_BETWEEN_MATCHES is enabled)
    if (RLProfilePicturesConstants::CLEAR_AVATARS_BETWEEN_MATCHES) {
        gameWrapper->HookEvent("Function TAGame.GameEvent_Soccar_TA.InitGame", [this](std::string eventName) {
            RLProfilePicturesLogger::LogDebug("Match started - clearing avatar cache");
            avatarManager->ClearCache();
        });
    }
}

void RLProfilePicturesREVAMP::LoadStartupAvatar() {
    gameWrapper->Execute([this](GameWrapper* gw) {
        if (!gw || !*enabled) return;

        try {
            // Get local player's ID
            FUniqueNetId* localId = RL::GetPrimaryPlayerID();
            if (localId && static_cast<EOnlinePlatform>(localId->Platform) == EOnlinePlatform::OnlinePlatform_Epic) {
                // Local player is on Epic, pre-fetch their avatar from CDN
                RLProfilePicturesLogger::LogInfo("Local player is on Epic platform, pre-fetching avatar from CDN");
                std::string epicId = localId->EpicAccountId.ToString();

                if (!epicId.empty()) {
                    LoadEpicAvatarFromCDN(epicId, *localId);
                }
                else {
                    RLProfilePicturesLogger::LogError("Empty Epic ID for local player");
                    LoadLocalAvatarFallback();
                }
            }
            else {
                // Local player is not on Epic or ID not available, use local avatar file
                RLProfilePicturesLogger::LogInfo("Local player is not on Epic platform, loading local avatar file");
                LoadLocalAvatarFallback();
            }
        }
        catch (...) {
            RLProfilePicturesLogger::LogError("Exception occurred while loading avatar, falling back to local file");
            LoadLocalAvatarFallback();
        }
    });
}

void RLProfilePicturesREVAMP::LoadEpicAvatarFromCDN(const std::string& epicId, FUniqueNetId localId) {
    // Download the Epic avatar for local player
    std::string url = std::string(RLProfilePicturesConstants::API_BASE_URL) + 
                     RLProfilePicturesConstants::API_EPIC_RETRIEVE + epicId;

    CurlRequest req;
    req.url = url;
    req.verb = "GET";

    HttpWrapper::SendCurlRequest(req, [this, localId, epicId](int http_code, char* data_ptr, size_t data_size) {
        if (http_code != 200) {
            RLProfilePicturesLogger::LogError("Failed to fetch Epic avatar for local player. HTTP code: " + std::to_string(http_code));
            LoadLocalAvatarFallback();
            return;
        }

        if (data_ptr == nullptr || data_size == 0) {
            RLProfilePicturesLogger::LogError("No Epic avatar data received for local player");
            LoadLocalAvatarFallback();
            return;
        }

        std::vector<uint8_t> data(data_ptr, data_ptr + data_size);

        gameWrapper->Execute([this, localId, data, epicId](GameWrapper* gw) {
            RLProfilePicturesLogger::LogSuccess("Epic avatar downloaded for local player: " + epicId);

            try {
                // Apply brightness adjustment and load as local avatar
                std::vector<uint8_t> brightenedData = RLProfilePicturesImageProcessor::BrightenImage(data, brightness_enabled);

                // Create temporary file
                std::filesystem::path filePath = RLProfilePicturesFileUtils::GetTempLocalAvatarPath(epicId);

                {
                    std::ofstream out(filePath, std::ios::binary);
                    if (out) {
                        out.write(reinterpret_cast<const char*>(brightenedData.data()), brightenedData.size());
                        out.flush();
                    }
                }

                // Load the image and apply it as local avatar
                auto img = std::make_unique<ImageWrapper>(filePath, true, false);
                if (img->LoadForCanvas()) {
                    UTexture2D* newTexture = static_cast<UTexture2D*>(img->GetCanvasTex());
                    if (newTexture) {
                        // Apply to local player 
                        UVanitySetManager_TA* vman = RL::GetVanitySetManager();
                        APlayerControllerBase_TA* pc = RL::GetPlayerController();

                        if (pc && vman) {
                            UPlayerAvatar_TA* avatar = vman->GetAvatar(localId);
                            if (avatar) {
                                pc->PlayerAvatar = avatar;
                                avatar->HandleUpdateTexture(newTexture);
                                vman->HandleLoadedAvatarAsset(avatar);

                                UGFxShell_X* shell = RL::GetShell();
                                if (shell) {
                                    UGFxData_PlayerAvatar_TA* avatarData = UGFxData_PlayerAvatar_TA::GetOrCreate(shell, avatar);
                                    UGFxDataStore_X* dataStore = shell->DataStore;
                                    if (dataStore && avatarData) {
                                        dataStore->SetTextureValue(avatarData->TableName, avatarData->RowIndex, L"ToPlayer", newTexture);
                                    }
                                }

                                RLProfilePicturesLogger::LogSuccess("Brightened local Epic avatar applied successfully!");
                            }
                        }
                    }
                }

                // Clean up temporary file
                std::filesystem::remove(filePath);
            }
            catch (const std::exception& e) {
                RLProfilePicturesLogger::LogError("Exception in Epic avatar brightness processing: " + std::string(e.what()));
                std::filesystem::path filePath = RLProfilePicturesFileUtils::GetTempLocalAvatarPath(epicId);
                std::filesystem::remove(filePath);
            }
        });
    });
}

void RLProfilePicturesREVAMP::LoadLocalAvatarFallback() {
    std::string avatarPathFromCvar = cvarManager->getCvar(RLProfilePicturesConstants::CVAR_AVATAR_PATH).getStringValue();

    if (avatarPathFromCvar.empty() || avatarPathFromCvar == RLProfilePicturesConstants::DEFAULT_AVATAR_PATH) {
        RLProfilePicturesLogger::LogInfo("No local avatar file selected, skipping avatar load");
        return;
    }

    try {
        avatarManager->AddLocalAvatar(avatarPathFromCvar);
        RLProfilePicturesLogger::LogSuccess("Local avatar file loaded as fallback");
    }
    catch (...) {
        RLProfilePicturesLogger::LogError("Failed to load local avatar file!");
    }
}

void RLProfilePicturesREVAMP::RenderSettings() {
    settingsUI->RenderSettings(enabled, debug_logs, steam_enabled, epic_enabled, 
                              xbox_enabled, psn_enabled, switch_enabled, avatar_path, brightness_enabled, default_avatars_enabled);
}