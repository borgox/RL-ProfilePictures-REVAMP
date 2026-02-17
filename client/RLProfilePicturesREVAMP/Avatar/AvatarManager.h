#pragma once

#include "RLSDK/SdkHeaders.hpp"
#include "AvatarDownloader.h"
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <cstdint>

// Forward declarations
class GameWrapper;

// =============================================================================
// AVATAR MANAGER
// =============================================================================

class AvatarManager {
private:
    std::shared_ptr<GameWrapper> gameWrapper;
    std::unique_ptr<AvatarDownloader> downloader;

    // Avatar cache: maps ID strings to texture pointers
    std::map<std::string, UTexture2DDynamic*> avatar_cache;

    /**
     * Gets brightness adjustment setting from CVar
     * @return shared_ptr to brightness enabled setting, or nullptr if not available
     */
    std::shared_ptr<bool> GetBrightnessEnabled();

	void ApplyAvatar(UPlayerAvatar_TA* avatar, UTexture2DDynamic* tex);

public:
    /**
     * Constructor
     * @param gw GameWrapper instance for thread-safe operations
     */
    explicit AvatarManager(std::shared_ptr<GameWrapper> gw);

    /**
     * Destructor - cleans up resources
     */
    ~AvatarManager();

    /**
     * Adds a local avatar from file path
     * Applies brightness adjustment and uploads to CDN for Epic players
     * Must be called from game thread
     *
     * @param filePath Path to the local avatar image file
     */
    void AddLocalAvatar(const std::filesystem::path& filePath);

    void LoadAvatarDirect(FUniqueNetId id, const std::string& idString, const std::vector<uint8_t>& alreadyProcessedData, bool forceUpdate = false);

    /**
     * Removes the local player's avatar
     * Must be called from game thread
     */
    void RemoveLocalAvatar();

    /**
     * Loads an avatar for a remote player from downloaded data
     * Applies brightness adjustment and caches the result
     * Must be called from game thread
     *
     * @param id Unique network ID of the player
     * @param data Raw PNG image data
     */
    void LoadAvatar(FUniqueNetId id, const std::vector<uint8_t>& data);

    /**
     * Sets an avatar texture for a specific player
     * Updates all necessary game components and UI elements
     * Must be called from game thread
     *
     * @param id Unique network ID of the player
     * @param tex Texture to apply
     */
    void SetAvatar(FUniqueNetId id, UTexture2DDynamic* tex);

    /**
     * Removes an avatar for a specific player
     * Must be called from game thread
     *
     * @param id Unique network ID of the player
     */
    void RemoveUserAvatar(FUniqueNetId id);

    /**
     * Processes a PRI (Player Replication Info) for avatar loading
     * Determines the appropriate download method based on platform
     * Must be called from game thread
     *
     * @param pri Player Replication Info object
     */
    void LoadForPRI(APRI_TA* pri);

    /**
     * Clears all cached avatars
     * Used when CLEAR_AVATARS_BETWEEN_MATCHES is enabled
     */
    void ClearCache();

    /**
     * Checks if an avatar is cached for the given ID
     * @param idString String representation of the unique ID
     * @return true if avatar is cached
     */
    bool IsAvatarCached(const std::string& idString);

    /**
     * Gets a cached avatar texture
     * @param idString String representation of the unique ID
     * @return Cached texture or nullptr if not found
     */
    UTexture2DDynamic* GetCachedAvatar(const std::string& idString);
};