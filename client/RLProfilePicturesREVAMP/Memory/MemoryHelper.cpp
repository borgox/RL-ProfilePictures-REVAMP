#include "pch.h"
#include "MemoryHelper.h"
#include "../Config/Constants.h"
// windows.h is included via pch.h
#include <tlhelp32.h>
#include <psapi.h>
#include <iostream>
#include <vector>

// =============================================================================
// MEMORY HELPER IMPLEMENTATION
// =============================================================================

MemoryHelper::MemoryHelper() {
    GetProcess();
    processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, processId);
    
    // exit(0) is intentional 
    if (processHandle == NULL) {
        std::cout << "Failed to open process." << std::endl;
        exit(0);
    }
    
    // Get base address of the main module
    HMODULE hMods[1024];
    DWORD cbNeeded;
    if (EnumProcessModules(processHandle, hMods, sizeof(hMods), &cbNeeded)) {
        MODULEINFO modInfo;
        if (GetModuleInformation(processHandle, hMods[0], &modInfo, sizeof(modInfo))) {
            baseAddress = reinterpret_cast<uintptr_t>(modInfo.lpBaseOfDll);
        }
    }
}

MemoryHelper::~MemoryHelper() {
    if (processHandle != NULL) {
        CloseHandle(processHandle);
    }
}

uintptr_t MemoryHelper::GetBaseAddress() const {
    return baseAddress;
}

void MemoryHelper::GetProcess() {
    PROCESSENTRY32 processEntry;
    processEntry.dwSize = sizeof(PROCESSENTRY32);
    
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    
    if (Process32First(snapshot, &processEntry)) {
        do {
            std::wstring processNameW(processEntry.szExeFile);
            std::string currentProcessName(processNameW.begin(), processNameW.end());
            
            if (currentProcessName.find(processName) != std::string::npos) {
                processId = processEntry.th32ProcessID;
                CloseHandle(snapshot);
                return;
            }
        } while (Process32Next(snapshot, &processEntry));
    }
    
    CloseHandle(snapshot);
    // exit(0) is intentional
    std::cout << "Process not found." << std::endl;
    exit(0);
}

uintptr_t MemoryHelper::FindPattern(const std::string& pattern) {
    // Parse pattern string into bytes and wildcards
    std::vector<std::string> patternBytes;
    std::string token;
    for (size_t i = 0; i < pattern.length(); ++i) {
        if (pattern[i] == ' ') {
            if (!token.empty()) {
                patternBytes.push_back(token);
                token.clear();
            }
        }
        else {
            token += pattern[i];
        }
    }
    if (!token.empty()) {
        patternBytes.push_back(token);
    }
    
    std::vector<uint8_t> bytePattern(patternBytes.size());
    std::vector<bool> wildcard(patternBytes.size());
    
    for (size_t i = 0; i < patternBytes.size(); ++i) {
        if (patternBytes[i] == "??") {
            bytePattern[i] = 0x00;
            wildcard[i] = true;
        }
        else {
            bytePattern[i] = static_cast<uint8_t>(std::stoul(patternBytes[i], nullptr, 16));
            wildcard[i] = false;
        }
    }
    
    // Search through process memory
    MEMORY_BASIC_INFORMATION mbi;
    uintptr_t currentAddress = baseAddress;
    
    while (VirtualQueryEx(processHandle, reinterpret_cast<LPCVOID>(currentAddress), &mbi, sizeof(mbi))) {
        if (mbi.State == MEM_COMMIT && (mbi.Protect & PAGE_GUARD) == 0 && (mbi.Protect & PAGE_NOACCESS) == 0) {
            std::vector<uint8_t> buffer(mbi.RegionSize);
            SIZE_T bytesRead;
            
            if (ReadProcessMemory(processHandle, mbi.BaseAddress, buffer.data(), mbi.RegionSize, &bytesRead)) {
                for (size_t i = 0; i < bytesRead - bytePattern.size(); ++i) {
                    bool found = true;
                    for (size_t j = 0; j < bytePattern.size(); ++j) {
                        if (!wildcard[j] && bytePattern[j] != buffer[i + j]) {
                            found = false;
                            break;
                        }
                    }
                    
                    if (found) {
                        return reinterpret_cast<uintptr_t>(mbi.BaseAddress) + i;
                    }
                }
            }
        }
        
        currentAddress = reinterpret_cast<uintptr_t>(mbi.BaseAddress) + mbi.RegionSize;
    }
    
    // exit(0) is intentional
    std::cout << "Pattern not found in the process." << std::endl;
    exit(0);
    return 0;
}
