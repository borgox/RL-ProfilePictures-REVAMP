#pragma once

#include <string>
#include <vector>
#include <filesystem>

// =============================================================================
// FILE UTILITIES
// =============================================================================

namespace RLProfilePicturesFileUtils {
    
    /**
     * Ensures the temp directory exists, creates it if necessary
     * @return true if directory exists or was created successfully
     */
    bool EnsureTempDirectoryExists();
    
    /**
     * Opens a file dialog to select a PNG or JPG image
     * @param outPath [out] The selected file path
     * @return true if a file was selected, false if cancelled
     */
    bool OpenImageFileDialog(std::filesystem::path& outPath);
    
    /**
     * Sanitizes a filename by replacing invalid characters with underscores
     * @param filename The filename to sanitize
     * @return The sanitized filename
     */
    std::string SanitizeFilename(const std::string& filename);
    
    /**
     * Converts a wide string to UTF-8
     * @param w The wide string to convert
     * @return The UTF-8 string
     */
    std::string WStringToUtf8(const std::wstring& w);

    /**
     * Converts a UTF-8 string to wstring
     * @param str The UTF-8 string to convert
     * @return The wstring
     */
    std::wstring Utf8ToWString(const std::string& str);
    
    /**
     * Generates a temporary file path for avatar storage
     * @param idString The ID string to use in the filename
     * @return The full temporary file path
     */
    std::filesystem::path GetTempAvatarPath(const std::string& idString);
    
    /**
     * Generates a temporary file path for local avatar storage
     * @param idString The ID string to use in the filename
     * @return The full temporary file path
     */
    std::filesystem::path GetTempLocalAvatarPath(const std::string& idString);
    
    /**
     * Gets the standard brightened local avatar path
     * @return The full temporary file path for brightened local avatar
     */
    std::filesystem::path GetBrightenedLocalAvatarPath();

    /**
     * Gets the temporary directory path
     * @return The full path to temporary directory
     */
    std::filesystem::path GetTempDirectory();
}
