#pragma once

#include "GuiBase.h"
#include "bakkesmod/plugin/bakkesmodplugin.h"
#include "bakkesmod/plugin/pluginwindow.h"
#include "bakkesmod/plugin/PluginSettingsWindow.h"
#include "RLSDK/SdkHeaders.hpp"
#include "version.h"

// Forward declarations
class AvatarManager;
class SettingsUI;

// Plugin version constants
constexpr auto plugin_version = stringify(VERSION_MAJOR) "." stringify(VERSION_MINOR) "." stringify(VERSION_PATCH) "." stringify(VERSION_BUILD);
constexpr auto pretty_plugin_version = "v" stringify(VERSION_MAJOR) "." stringify(VERSION_MINOR) "." stringify(VERSION_PATCH);


class RLProfilePicturesREVAMP : public BakkesMod::Plugin::BakkesModPlugin, public SettingsWindowBase {
public:
    // BakkesModPlugin overrides
    void onLoad() override;
    void RenderSettings() override;
    std::string GetPluginName() override { return "RLProfilePicturesREVAMP"; }

private:
    // =============================================================================
    // MODULE INSTANCES
    // =============================================================================
    
    std::shared_ptr<AvatarManager> avatarManager;
    std::unique_ptr<SettingsUI> settingsUI;

    // =============================================================================
    // CONFIGURATION VARIABLES
    // =============================================================================

    // Main plugin settings
    std::shared_ptr<bool> enabled = std::make_shared<bool>(true);
    std::shared_ptr<bool> debug_logs = std::make_shared<bool>(true);
    std::shared_ptr<std::string> avatar_path_string = std::make_shared<std::string>();
    std::shared_ptr<std::filesystem::path> avatar_path = std::make_shared<std::filesystem::path>();

    // Platform-specific settings
    std::shared_ptr<bool> steam_enabled = std::make_shared<bool>(true);
    std::shared_ptr<bool> epic_enabled = std::make_shared<bool>(true);
    std::shared_ptr<bool> xbox_enabled = std::make_shared<bool>(true);
    std::shared_ptr<bool> psn_enabled = std::make_shared<bool>(true);
    std::shared_ptr<bool> switch_enabled = std::make_shared<bool>(true);
	std::shared_ptr<bool> brightness_enabled = std::make_shared<bool>(true);

	std::shared_ptr<bool> default_avatars_enabled = std::make_shared<bool>(false);
    // =============================================================================
    // INITIALIZATION FUNCTIONS
    // =============================================================================

    /**
     * Initializes all CVars for the plugin
     */
    void InitializeCVars();
    
    /**
     * Initializes the modules (AvatarManager, SettingsUI, etc.)
     */
    void InitializeModules();
    
    /**
     * Registers event hooks for avatar loading
     */
    void RegisterEventHooks();
    
    /**
     * Loads avatar on plugin startup
     */
    void LoadStartupAvatar();
    
    /**
     * Loads Epic avatar from CDN for local player
     */
    void LoadEpicAvatarFromCDN(const std::string& epicId, FUniqueNetId localId);
    
    /**
     * Fallback to load local avatar file
     */
    void LoadLocalAvatarFallback();
};