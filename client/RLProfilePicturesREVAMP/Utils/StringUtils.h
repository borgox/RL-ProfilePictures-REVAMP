#pragma once

#include <string>

// =============================================================================
// STRING UTILITIES
// =============================================================================

namespace RLProfilePicturesStringUtils {
    
    /**
     * Sanitizes a filename by replacing invalid characters with underscores
     * @param filename The filename to sanitize
     * @return The sanitized filename
     */
    std::string SanitizeFilename(const std::string& filename);
}
