#include "pch.h"
#include "Logger.h"
#include "../Config/Constants.h"

// =============================================================================
// LOGGER
// =============================================================================

namespace RLProfilePicturesLogger {
    
    // Static variables for logger state
    static std::shared_ptr<CVarManagerWrapper> s_cvarManager = nullptr;
    static std::shared_ptr<bool> s_debugLogsEnabled = nullptr;
    
    void Initialize(std::shared_ptr<CVarManagerWrapper> cvarManager, std::shared_ptr<bool> debugLogsEnabled) {
        s_cvarManager = cvarManager;
        s_debugLogsEnabled = debugLogsEnabled;
    }
    
    void LogInfo(const std::string& message) {
        if (s_cvarManager) {
            s_cvarManager->log("\x1b[38;2;102;204;255m[INFO] " + message + "\x1b[39m");
        }
    }
    
    void LogSuccess(const std::string& message) {
        if (s_cvarManager) {
            s_cvarManager->log("\x1b[38;2;102;255;102m[SUCCESS] " + message + "\x1b[39m");
        }
    }
    
    void LogError(const std::string& message) {
        if (s_cvarManager) {
            s_cvarManager->log("\x1b[38;2;255;102;102m[ERROR] " + message + "\x1b[39m");
        }
    }
    
    void LogDebug(const std::string& message) {
        if (!s_cvarManager) return;
        
        // Check if debug logs are enabled via the shared bool pointer
        if (s_debugLogsEnabled && *s_debugLogsEnabled) {
            s_cvarManager->log("\x1b[38;2;255;255;102m[DEBUG] " + message + "\x1b[39m");
            return;
        }
        
        // Fallback: check the CVar directly
        CVarWrapper debugCVar = s_cvarManager->getCvar(RLProfilePicturesConstants::CVAR_DEBUG_LOGS);
        if (!debugCVar.IsNull() && debugCVar.getBoolValue()) {
            s_cvarManager->log("\x1b[38;2;255;255;102m[DEBUG] " + message + "\x1b[39m");
        }
    }
}
