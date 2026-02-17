#include "pch.h"
#include "SettingsUI.h"
#include "../Config/Constants.h"
#include "../Utils/FileUtils.h"
#include "../Avatar/AvatarManager.h"
#include "../version.h"

// Plugin version constants (defined here to avoid circular dependencies)
constexpr auto pretty_plugin_version = "v" stringify(VERSION_MAJOR) "." stringify(VERSION_MINOR) "." stringify(VERSION_PATCH);

// =============================================================================
// SETTINGS UI IMPLEMENTATION
// =============================================================================

// Static UI state
float SettingsUI::feedbackTime = 0.0f;
std::string SettingsUI::feedbackMessage = "";

SettingsUI::SettingsUI(std::shared_ptr<GameWrapper> gw, std::shared_ptr<AvatarManager> avatarMgr) 
    : gameWrapper(gw), avatarManager(avatarMgr) {}

void SettingsUI::RenderOption(const char* label, const char* cvarName, 
                             std::shared_ptr<bool> value, const float color[4], const char* tooltip) {
    extern std::shared_ptr<CVarManagerWrapper> _globalCvarManager;
    
    ImGui::TextColored(ImVec4(color[0], color[1], color[2], color[3]), label);
    ImGui::NextColumn();
    if (ImGui::Checkbox(("##" + std::string(label)).c_str(), value.get())) {
        if (_globalCvarManager) {
            _globalCvarManager->getCvar(cvarName).setValue(*value);
        }
    }
    if (ImGui::IsItemHovered(65536)) {
        ImGui::SetTooltip(tooltip);
    }
    ImGui::NextColumn();
}

void SettingsUI::RenderPlatformOption(const char* prefix, const char* platform, const char* suffix,
                                     const char* cvarName, std::shared_ptr<bool> value, const float color[4], const char* tooltip) {
    extern std::shared_ptr<CVarManagerWrapper> _globalCvarManager;
    
    ImGui::TextUnformatted(prefix);
    ImGui::SameLine(0.0f, 0.0f);
    ImGui::TextColored(ImVec4(color[0], color[1], color[2], color[3]), "%s", platform);
    ImGui::SameLine(0.0f, 0.0f);
    ImGui::TextUnformatted(suffix);
    ImGui::NextColumn();
    if (ImGui::Checkbox(("##" + std::string(prefix) + platform + suffix).c_str(), value.get())) {
        if (_globalCvarManager) {
            _globalCvarManager->getCvar(cvarName).setValue(*value);
        }
    }
    if (ImGui::IsItemHovered(65536)) {
        ImGui::SetTooltip(tooltip);
    }
    ImGui::NextColumn();
}

void SettingsUI::RenderSettings(std::shared_ptr<bool> enabled,
                               std::shared_ptr<bool> debug_logs,
                               std::shared_ptr<bool> steam_enabled,
                               std::shared_ptr<bool> epic_enabled,
                               std::shared_ptr<bool> xbox_enabled,
                               std::shared_ptr<bool> psn_enabled,
                               std::shared_ptr<bool> switch_enabled,
                               std::shared_ptr<std::filesystem::path> avatar_path,
                               std::shared_ptr<bool> brightness_enabled,
                               std::shared_ptr<bool> default_avatars_enabled) {
    extern std::shared_ptr<CVarManagerWrapper> _globalCvarManager;
    
    // Header section
    if (ImGui::BeginChild("Header", ImVec2(0, RLProfilePicturesConstants::HEADER_HEIGHT), true)) {
        // Add some spacing
        for (int i = 0; i < 4; i++) {
            ImGui::Spacing();
        }
        ImGui::TextColored(ImVec4(1.0f, 0.0f, 0.0f, 1.0f), "Plugin made by borgox (@borghetoo on dc)");
        for (int i = 0; i < 5; i++) {
            ImGui::Spacing();
        }
        ImGui::Text(pretty_plugin_version);
    }
    ImGui::EndChild();
    
    // Settings checkboxes
    if (ImGui::BeginChild("Checkboxes", ImVec2(0, RLProfilePicturesConstants::CHECKBOXES_HEIGHT), true)) {
        ImGui::Columns(2, nullptr, false);
        ImGui::SetColumnWidth(0, RLProfilePicturesConstants::COLUMN_WIDTH);
        
        // Render all options using the helper functions
        RenderOption("Enable RLProfilePicturesREVAMP", 
                    RLProfilePicturesConstants::CVAR_ENABLED, 
                    enabled, 
                    RLProfilePicturesConstants::COLOR_MAIN,
                    RLProfilePicturesConstants::CVAR_ENABLED_TOOLTIP);
                    
        RenderOption("Enable Debug Logs", 
                    RLProfilePicturesConstants::CVAR_DEBUG_LOGS, 
                    debug_logs, 
                    RLProfilePicturesConstants::COLOR_DEBUG,
                    RLProfilePicturesConstants::CVAR_DEBUG_LOGS_TOOLTIP);
                    
        RenderPlatformOption("Enable ", "Steam", " Profile Pictures", 
                           RLProfilePicturesConstants::CVAR_STEAM_ENABLED, 
                           steam_enabled, 
                           RLProfilePicturesConstants::COLOR_STEAM,
                           RLProfilePicturesConstants::CVAR_STEAM_ENABLED_TOOLTIP);
                           
        RenderPlatformOption("Enable ", "Epic", " Profile Pictures", 
                           RLProfilePicturesConstants::CVAR_EPIC_ENABLED, 
                           epic_enabled, 
                           RLProfilePicturesConstants::COLOR_EPIC,
                           RLProfilePicturesConstants::CVAR_EPIC_ENABLED_TOOLTIP);
                           
        RenderPlatformOption("Enable ", "Xbox", " Profile Pictures", 
                           RLProfilePicturesConstants::CVAR_XBOX_ENABLED, 
                           xbox_enabled, 
                           RLProfilePicturesConstants::COLOR_XBOX,
                           RLProfilePicturesConstants::CVAR_XBOX_ENABLED_TOOLTIP);
                           
        RenderPlatformOption("Enable ", "PSN", " Profile Pictures", 
                           RLProfilePicturesConstants::CVAR_PSN_ENABLED, 
                           psn_enabled, 
                           RLProfilePicturesConstants::COLOR_PSN,
                           RLProfilePicturesConstants::CVAR_PSN_ENABLED_TOOLTIP);
                           
        RenderPlatformOption("Enable ", "Switch", " Profile Pictures", 
                           RLProfilePicturesConstants::CVAR_SWITCH_ENABLED, 
                           switch_enabled, 
                           RLProfilePicturesConstants::COLOR_SWITCH,
                           RLProfilePicturesConstants::CVAR_SWITCH_ENABLED_TOOLTIP );
        RenderPlatformOption("Enable ", "Default", "Avatars", 
                           RLProfilePicturesConstants::CVAR_LOAD_DEFAULT_AVATARS, 
			               default_avatars_enabled,
			               RLProfilePicturesConstants::COLOR_DEFAULT_IMAGES,
                           RLProfilePicturesConstants::CVAR_LOAD_DEFAULT_AVATARS_TOOLTIP);
        RenderPlatformOption("Enable ", "Brightness Adjustment", "", 
                           RLProfilePicturesConstants::CVAR_BRIGHTNESS_ADJUSTMENT_ENABLED, 
                           brightness_enabled, 
			               RLProfilePicturesConstants::COLOR_BRIGHTNESS,
                           RLProfilePicturesConstants::CVAR_BRIGHTNESS_ADJUSTMENT_ENABLED_TOOLTIP);
        ImGui::Columns(1);
    }
    ImGui::EndChild();
    
    // Local avatar controls
    if (ImGui::BeginChild("Local Avatar", ImVec2(0, RLProfilePicturesConstants::LOCAL_AVATAR_HEIGHT), true)) {
        if (ImGui::Button("Select Avatar Image (.png, .jpg, .jpeg)")) {
            std::filesystem::path imagePath;
            if (RLProfilePicturesFileUtils::OpenImageFileDialog(imagePath)) {
                *avatar_path = imagePath;
                if (_globalCvarManager) {
                    _globalCvarManager->getCvar(RLProfilePicturesConstants::CVAR_AVATAR_PATH).setValue(RLProfilePicturesFileUtils::WStringToUtf8(imagePath.c_str()));
                }
                
                gameWrapper->Execute([this, imagePath](GameWrapper* gw) {
                    if (!gw) return;
                    try {
                        avatarManager->AddLocalAvatar(imagePath);
                        SetFeedback("Avatar updated successfully!");
                    }
                    catch (...) {
                        SetFeedback("Failed to update avatar.");
                    }
                });
            }
        }
        
        ImGui::SameLine();
        
        if (ImGui::Button("Remove Avatar")) {
            gameWrapper->Execute([this](GameWrapper* gw) {
                if (!gw) return;
                try {
                    avatarManager->RemoveLocalAvatar();
                    SetFeedback("Avatar removed successfully!");
                }
                catch (...) {
                    SetFeedback("Failed to remove avatar.");
                }
            });
        }
        
        // Add some spacing
        for (int i = 0; i < 2; i++) {
            ImGui::Spacing();
        }
        
        // Display feedback message
        if (!feedbackMessage.empty() && 
            ImGui::GetTime() - feedbackTime < RLProfilePicturesConstants::FEEDBACK_DURATION) {
            ImGui::TextColored(ImVec4(RLProfilePicturesConstants::COLOR_SUCCESS[0],
                                     RLProfilePicturesConstants::COLOR_SUCCESS[1],
                                     RLProfilePicturesConstants::COLOR_SUCCESS[2],
                                     RLProfilePicturesConstants::COLOR_SUCCESS[3]), 
                              "%s", feedbackMessage.c_str());
        }
        else if (ImGui::GetTime() - feedbackTime >= RLProfilePicturesConstants::FEEDBACK_DURATION) {
            feedbackMessage = "";
        }
    }
    ImGui::EndChild();
    
    // Add spacing and separator
    ImGui::Spacing();
    ImGui::Separator();
    ImGui::TextWrapped("This plugin is still in development, expect bugs and missing features.");
}

void SettingsUI::SetFeedback(const std::string& message) {
    feedbackMessage = message;
    feedbackTime = ImGui::GetTime();
}
