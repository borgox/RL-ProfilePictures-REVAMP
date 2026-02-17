#pragma once

#include "RLSDK/SdkHeaders.hpp"
#include <string>
#include <vector>
#include <cstdint>
#include <functional>

// Forward declaration
class GameWrapper;

// =============================================================================
// AVATAR DOWNLOADER
// =============================================================================

class AvatarDownloader {
private:
    std::shared_ptr<GameWrapper> gameWrapper;
    std::function<void(FUniqueNetId, const std::vector<uint8_t>&)> loadAvatarCallback;
    
    /**
     * Generates the appropriate API URL for a given unique network ID
     * @param id The unique network ID
     * @return API URL string, or empty string if platform not supported
     */
    std::string GetURLForID(FUniqueNetId id);
    
    /**
     * Checks if avatar downloads are allowed for the given platform/ID
     * Considers platform-specific settings and local player platform
     * @param id The unique network ID to check
     * @return true if downloads are allowed for this ID
     */
    bool IsAllowed(FUniqueNetId id);

public:
    /**
     * Constructor
     * @param gw GameWrapper instance for thread-safe operations
     * @param callback Function to call when avatar data is downloaded
     */
    AvatarDownloader(std::shared_ptr<GameWrapper> gw, 
                    std::function<void(FUniqueNetId, const std::vector<uint8_t>&)> callback);
    
    /**
     * Downloads an avatar for the specified unique network ID
     * Handles all platforms except Xbox (which uses player names)
     * Uses gameWrapper->Execute for thread safety
     * 
     * @param id The unique network ID to download avatar for
     */
    void DownloadAvatar(FUniqueNetId id);
    
    /**
     * Downloads an Xbox avatar using the player's display name
     * Xbox platform requires player names instead of numeric IDs
     * Uses gameWrapper->Execute for thread safety
     * 
     * @param id The unique network ID 
     * @param playername The Xbox player's display name
     */
    void DownloadXboxAvatar(FUniqueNetId id, std::string playername);
    
    /**
     * Uploads a local avatar image to the CDN for Epic players
     * @param filePath Path to the local image file
     * @param epic_id Epic account ID string
     */
    void UploadToCDN(const std::filesystem::path& filePath,
        const std::string& epic_id,
        std::function<void(bool)> callback);
};
