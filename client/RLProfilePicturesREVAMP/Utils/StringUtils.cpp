#include "pch.h"
#include "StringUtils.h"

// =============================================================================
// STRING UTILITIES 
// =============================================================================

namespace RLProfilePicturesStringUtils {
    
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
}
