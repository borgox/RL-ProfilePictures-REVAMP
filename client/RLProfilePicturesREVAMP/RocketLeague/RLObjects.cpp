#include "pch.h"
#include "RLObjects.h"
#include "RLSDK/GameDefines.hpp"

// =============================================================================
// ROCKET LEAGUE OBJECT GETTERS 
// =============================================================================

namespace RL {
    
    UGameEngine_TA* GetRLGameEngine() {
        return reinterpret_cast<UGameEngine_TA*>(UEngine::GetEngine());
    }
    
    ULocalPlayer_TA* GetLocalPlayer(int index) {
        UGameEngine_TA* engine = GetRLGameEngine();
        if (!engine || engine->GamePlayers.size() <= index) return nullptr;
        return reinterpret_cast<ULocalPlayer_TA*>(engine->GamePlayers[index]);
    }
    
    APlayerControllerBase_TA* GetPlayerController(int index) {
        ULocalPlayer_TA* lp = GetLocalPlayer(index);
        if (!lp) return nullptr;
        return reinterpret_cast<APlayerControllerBase_TA*>(lp->Actor);
    }
    
    AHUDBase_TA* GetHUD(int index) {
        APlayerControllerBase_TA* pc = GetPlayerController(index);
        if (!pc) return nullptr;
        return reinterpret_cast<AHUDBase_TA*>(pc->myHUD);
    }
    
    UGFxShell_TA* GetShell(int index) {
        AHUDBase_TA* hud = GetHUD(index);
        if (!hud) return nullptr;
        return reinterpret_cast<UGFxShell_TA*>(hud->Shell);
    }
    
    UEngineShare_TA* GetEngineShare() {
        UGameEngine_TA* engine = GetRLGameEngine();
        if (!engine) return nullptr;
        return reinterpret_cast<UEngineShare_TA*>(engine->EngineShare);
    }
    
    UVanitySetManager_TA* GetVanitySetManager() {
        static UVanitySetManager_TA* vanityManager = nullptr;
        if (!vanityManager || !vanityManager->IsValid() || !vanityManager->IsA<UVanitySetManager_TA>()) {
            APlayerControllerBase_TA* pc = GetPlayerController();
            if (pc)
                vanityManager = pc->VanityMgr;
        }
        return vanityManager;
    }

    
    FUniqueNetId* GetPrimaryPlayerID() {
        UGameEngine_TA* engine = GetRLGameEngine();
        if (!engine) return nullptr;
        
        UEngineShare_TA* share = reinterpret_cast<UEngineShare_TA*>(engine->EngineShare);
        if (!share) return nullptr;
        
        UOnlineGame_TA* onlineGame = reinterpret_cast<UOnlineGame_TA*>(share->OnlineGame);
        if (!onlineGame || onlineGame->OnlinePlayers.size() == 0) return nullptr;
        
        UOnlinePlayer_X* player = onlineGame->OnlinePlayers[0];
        if (!player) return nullptr;
        
        return &player->PlayerID;
    }
}
