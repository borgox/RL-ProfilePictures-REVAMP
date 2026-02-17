#pragma once

#include <vector>
#include <cstdint>

// =============================================================================
// IMAGE PROCESSOR
// =============================================================================

namespace RLProfilePicturesImageProcessor {
    
    /**
     * Applies brightness/gamma correction to a PNG image
     * Decompresses PNG data, applies sRGB gamma correction, and recompresses
     * 
     * @param pngData The input PNG data as a byte vector
     * @return The processed PNG data as a byte vector
     * @throws std::runtime_error if image processing fails
     */
    std::vector<uint8_t> BrightenImage(const std::vector<uint8_t>& pngData,
        const std::shared_ptr<bool>& brightnessEnabled = nullptr);
}
