#pragma once

#include <string>
#include <memory>

// Forward declarations
class GameWrapper;
class AvatarManager;

// =============================================================================
// SETTINGS UI 
// =============================================================================

class SettingsUI {
private:
    std::shared_ptr<GameWrapper> gameWrapper;
    std::shared_ptr<AvatarManager> avatarManager;
    
    // UI state
    static float feedbackTime;
    static std::string feedbackMessage;
    
    /**
     * Renders a platform-specific checkbox option
     */
    void RenderPlatformOption(const char* prefix, const char* platform, const char* suffix,
                             const char* cvarName, std::shared_ptr<bool> value, const float color[4], const char* tooltip);
    
    /**
     * Renders a standard checkbox option
     */
    void RenderOption(const char* label, const char* cvarName, 
                     std::shared_ptr<bool> value, const float color[4], const char* tooltip);

public:
    /**
     * Constructor
     * @param gw GameWrapper instance
     * @param avatarMgr AvatarManager instance
     */
    SettingsUI(std::shared_ptr<GameWrapper> gw, std::shared_ptr<AvatarManager> avatarMgr);
    
    /**
     * Renders the complete settings window
     * @param enabled Plugin enabled state
     * @param debug_logs Debug logging enabled state
     * @param steam_enabled Steam platform enabled state
     * @param epic_enabled Epic platform enabled state
     * @param xbox_enabled Xbox platform enabled state
     * @param psn_enabled PSN platform enabled state
     * @param switch_enabled Switch platform enabled state
     * @param avatar_path Current avatar path
	 * @param brightness_enabled Brightness adjustment enabled state
	 * @param default_avatars_enabled Default avatars enabled state
     */
    void RenderSettings(std::shared_ptr<bool> enabled,
                       std::shared_ptr<bool> debug_logs,
                       std::shared_ptr<bool> steam_enabled,
                       std::shared_ptr<bool> epic_enabled,
                       std::shared_ptr<bool> xbox_enabled,
                       std::shared_ptr<bool> psn_enabled,
                       std::shared_ptr<bool> switch_enabled,
                       std::shared_ptr<std::filesystem::path> avatar_path,
                       std::shared_ptr<bool> brightness_enabled,
                       std::shared_ptr<bool> default_avatars_enabled);
    
    /**
     * Sets feedback message for UI display
     * @param message The message to display
     */
    void SetFeedback(const std::string& message);
};
