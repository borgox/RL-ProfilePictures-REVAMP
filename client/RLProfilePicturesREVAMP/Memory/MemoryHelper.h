#pragma once

#include <string>
// windows.h is included via pch.h

// =============================================================================
// MEMORY HELPER
// =============================================================================

class MemoryHelper {
private:
    std::string processName = "RocketLeague";
    HANDLE processHandle;
    DWORD processId;
    uintptr_t baseAddress;
    
    /**
     * Finds the RocketLeague process and stores its ID
     * Calls exit(0) on failure
     */
    void GetProcess();

public:
    /**
     * Constructor - initializes process access and base address
     * Calls exit(0) on failure
     */
    MemoryHelper();
    
    /**
     * Destructor - cleans up process handle
     */
    ~MemoryHelper();
    
    /**
     * Gets the base address of the RocketLeague process
     * @return Base address as uintptr_t
     */
    uintptr_t GetBaseAddress() const;
    
    /**
     * Reads memory from the target process
     * @param address Memory address to read from
     * @return Value of type T, or default-constructed T on failure
     */
    template<typename T>
    T ReadMemory(uintptr_t address);
    
    /**
     * Attempts to read memory with error checking
     * @param address Memory address to read from
     * @param result [out] The result if successful
     * @return true if read was successful, false otherwise
     */
    template<typename T>
    bool TryReadMemory(uintptr_t address, T& result);
    
    /**
     * @param pattern Hex pattern string (e.g., "?? ?? ?? ?? ?? ?? 00 00")
     * @return Address of found pattern, or calls exit(0) on failure
     */
    uintptr_t FindPattern(const std::string& pattern);
};

// Template implementations
template<typename T>
T MemoryHelper::ReadMemory(uintptr_t address) {
    T result = {};
    SIZE_T bytesRead;
    
    if (!ReadProcessMemory(processHandle, reinterpret_cast<LPCVOID>(address), &result, sizeof(T), &bytesRead)) {
        return result;
    }
    
    if (bytesRead != sizeof(T)) {
        return result;
    }
    
    return result;
}

template<typename T>
bool MemoryHelper::TryReadMemory(uintptr_t address, T& result) {
    SIZE_T bytesRead;
    
    if (!ReadProcessMemory(processHandle, reinterpret_cast<LPCVOID>(address), &result, sizeof(T), &bytesRead)) {
        return false;
    }
    
    return (bytesRead == sizeof(T));
}
