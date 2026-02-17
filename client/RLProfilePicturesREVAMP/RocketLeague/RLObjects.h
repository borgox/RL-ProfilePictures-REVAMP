#pragma once

#include "RLSDK/SdkHeaders.hpp"

// =============================================================================
// ROCKET LEAGUE OBJECT GETTERS
// =============================================================================

namespace RL {
    
    /**
     * Gets the main Rocket League game engine instance
     * @return Pointer to UGameEngine_TA or nullptr if not available
     */
    UGameEngine_TA* GetRLGameEngine();
    
    /**
     * Gets the local player instance
     * @param index Player index (default 0 for primary player)
     * @return Pointer to ULocalPlayer_TA or nullptr if not available
     */
    ULocalPlayer_TA* GetLocalPlayer(int index = 0);
    
    /**
     * Gets the player controller for specified player
     * @param index Player index (default 0 for primary player)
     * @return Pointer to APlayerControllerBase_TA or nullptr if not available
     */
    APlayerControllerBase_TA* GetPlayerController(int index = 0);
    
    /**
     * Gets the HUD instance for specified player
     * @param index Player index (default 0 for primary player)
     * @return Pointer to AHUDBase_TA or nullptr if not available
     */
    AHUDBase_TA* GetHUD(int index = 0);
    
    /**
     * Gets the GFx shell instance for specified player
     * @param index Player index (default 0 for primary player)
     * @return Pointer to UGFxShell_TA or nullptr if not available
     */
    UGFxShell_TA* GetShell(int index = 0);
    
    /**
     * Gets the engine share instance
     * @return Pointer to UEngineShare_TA or nullptr if not available
     */
    UEngineShare_TA* GetEngineShare();
    
    /**
     * Gets the vanity set manager instance
     * @return Pointer to UVanitySetManager_TA or nullptr if not available
     */
    UVanitySetManager_TA* GetVanitySetManager();
    
    /**
     * Gets the primary player's unique network ID
     * @return Pointer to FUniqueNetId or nullptr if not available
     */
    FUniqueNetId* GetPrimaryPlayerID();
}
