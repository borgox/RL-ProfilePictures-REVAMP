#pragma once

#include "bakkesmod/plugin/bakkesmodplugin.h"
#include <string>
#include <memory>

// =============================================================================
// LOGGER
// =============================================================================

namespace RLProfilePicturesLogger {
    
    /**
     * Initialize the logger with the CVarManager
     * Must be called during plugin initialization
     */
    void Initialize(std::shared_ptr<CVarManagerWrapper> cvarManager, std::shared_ptr<bool> debugLogsEnabled);
    
    /**
     * Log an informational message (blue color)
     */
    void LogInfo(const std::string& message);
    
    /**
     * Log a success message (green color)
     */
    void LogSuccess(const std::string& message);
    
    /**
     * Log an error message (red color)
     */
    void LogError(const std::string& message);
    
    /**
     * Log a debug message (yellow color)
     * Only displays if debug logging is enabled
     */
    void LogDebug(const std::string& message);
}
