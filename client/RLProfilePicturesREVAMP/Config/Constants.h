#pragma once

// =============================================================================
// CONFIGURATION CONSTANTS
// =============================================================================

namespace RLProfilePicturesConstants {
    // =============================================================================
    // PLUGIN CONFIGURATION
    // =============================================================================
    
    // Dev setting 
    constexpr bool CLEAR_AVATARS_BETWEEN_MATCHES = false;
    
    // Temporary file paths
    constexpr auto TEMP_DIRECTORY = "C:/Temp";
    constexpr auto TEMP_AVATAR_PREFIX = "avatar_";
    constexpr auto TEMP_LOCAL_AVATAR = "brightened_local_avatar.png";
    constexpr auto TEMP_LOCAL_PREFIX = "local_avatar_";
    
    // =============================================================================
    // API ENDPOINTS
    // =============================================================================
    
    constexpr auto API_BASE_URL = "https://api.borgox.tech/api/v1";
    constexpr auto API_STEAM_RETRIEVE = "/steam/retrieve/";
    constexpr auto API_EPIC_RETRIEVE = "/epic/retrieve/";
    constexpr auto API_EPIC_UPLOAD = "/epic/upload/";
    constexpr auto API_PSN_RETRIEVE = "/psn/retrieve/";
    constexpr auto API_SWITCH_RETRIEVE = "/switch/retrieve/";
    constexpr auto API_XBOX_RETRIEVE = "/xbox/retrieve/";
    
    // =============================================================================
    // CVAR NAMES
    // =============================================================================
    
    constexpr auto CVAR_ENABLED = "RLProfilePicturesREVAMP_Enabled";
    constexpr auto CVAR_DEBUG_LOGS = "RLProfilePicturesREVAMP_DebugLogs";
    constexpr auto CVAR_AVATAR_PATH = "RLProfilePicturesREVAMP_AvatarPath";
    constexpr auto CVAR_STEAM_ENABLED = "RLProfilePicturesREVAMP_Steam_Enabled";
    constexpr auto CVAR_EPIC_ENABLED = "RLProfilePicturesREVAMP_Epic_Enabled";
    constexpr auto CVAR_XBOX_ENABLED = "RLProfilePicturesREVAMP_Xbox_Enabled";
    constexpr auto CVAR_PSN_ENABLED = "RLProfilePicturesREVAMP_PSN_Enabled";
    constexpr auto CVAR_SWITCH_ENABLED = "RLProfilePicturesREVAMP_Switch_Enabled";
	constexpr auto CVAR_BRIGHTNESS_ADJUSTMENT_ENABLED = "RLProfilePicturesREVAMP_BrightnessAdjustment_Enabled"; 
    constexpr auto CVAR_LOAD_DEFAULT_AVATARS = "rlprofilepictures_load_default_avatars";


    // =============================================================================
    // CVARS TOOLTIPS
    // ============================================================================= 
	constexpr auto CVAR_ENABLED_TOOLTIP = "Enable the RLProfilePicturesREVAMP plugin";
	constexpr auto CVAR_DEBUG_LOGS_TOOLTIP = "Enable debug logs (Only for debugging purposes)";
	constexpr auto CVAR_AVATAR_PATH_TOOLTIP = "Path to local avatar image (.png, .jpg, .jpeg)";
	constexpr auto CVAR_STEAM_ENABLED_TOOLTIP = "Enable profile pictures for Steam players";
	constexpr auto CVAR_EPIC_ENABLED_TOOLTIP = "Enable profile pictures for Epic players";
	constexpr auto CVAR_XBOX_ENABLED_TOOLTIP = "Enable profile pictures for Xbox players";
	constexpr auto CVAR_PSN_ENABLED_TOOLTIP = "Enable profile pictures for PS4/PS5 players";
	constexpr auto CVAR_SWITCH_ENABLED_TOOLTIP = "Enable profile pictures for Switch players";
	constexpr auto CVAR_BRIGHTNESS_ADJUSTMENT_ENABLED_TOOLTIP = "Enable brightness adjustment for avatars (improves visibility if your images are too dark)";
	constexpr auto CVAR_LOAD_DEFAULT_AVATARS_TOOLTIP = "Load default avatars for players without custom avatars";


    // =============================================================================
    // MEMORY PATTERNS
    // =============================================================================
    
    // Pattern for GNames/GObjects
    constexpr auto GNAMES_PATTERN = "?? ?? ?? ?? ?? ?? 00 00 ?? ?? 01 00 35 25 02 00";
    constexpr auto GOBJ_OFFSET = 0x48;
    
    // =============================================================================
    // UI CONFIGURATION
    // =============================================================================
    
    // UI Colors (RGBA)
    constexpr float COLOR_MAIN[4] = {0.75f, 0.0f, 0.5f, 1.0f};
    constexpr float COLOR_DEBUG[4] = {1.0f, 1.0f, 0.0f, 1.0f};
    constexpr float COLOR_STEAM[4] = {0.2f, 0.6f, 1.0f, 1.0f};
    constexpr float COLOR_EPIC[4] = {0.75f, 0.75f, 0.75f, 1.0f};
    constexpr float COLOR_XBOX[4] = {0.0f, 0.8f, 0.0f, 1.0f};
    constexpr float COLOR_PSN[4] = {0.1f, 0.4f, 0.9f, 1.0f};
    constexpr float COLOR_SWITCH[4] = {0.9f, 0.1f, 0.1f, 1.0f};
	constexpr float COLOR_BRIGHTNESS[4] = { 1.0f, 0.5f, 0.0f, 1.0f };  
    constexpr float COLOR_SUCCESS[4] = {0.2f, 1.0f, 0.2f, 1.0f};
    constexpr float COLOR_DEFAULT_IMAGES[4] = { 0.29f, 0.0f, 0.51f, 1.0f }; // Indaco RGBA (hi emi yes this is italian)

    
    
    // UI Dimensions
    constexpr float HEADER_HEIGHT = 80.0f;
    constexpr float CHECKBOXES_HEIGHT = 230.0f;
    constexpr float LOCAL_AVATAR_HEIGHT = 60.0f;
    constexpr float COLUMN_WIDTH = 280.0f;
    constexpr float FEEDBACK_DURATION = 2.0f;
    
    // =============================================================================
    // IMAGE PROCESSING
    // =============================================================================
    
    // sRGB gamma correction exponent
    constexpr float GAMMA_CORRECTION_EXPONENT = 0.4545454545f;
    
    // =============================================================================
    // DEFAULT VALUES
    // =============================================================================
    
    constexpr auto DEFAULT_AVATAR_PATH = "No image selected";
    constexpr bool DEFAULT_ENABLED = true;
    constexpr bool DEFAULT_DEBUG_LOGS = true;
    constexpr bool DEFAULT_PLATFORM_ENABLED = true;
}
