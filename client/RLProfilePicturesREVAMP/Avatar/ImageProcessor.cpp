#include "pch.h"
#include "ImageProcessor.h"
#include "../Config/Constants.h"
#include "../Utils/Logger.h"
#include "stb_image.h"
#include "stb_image_write.h"
#include <stdexcept>
#include <memory>

// =============================================================================
// IMAGE PROCESSOR IMPLEMENTATION
// =============================================================================

namespace RLProfilePicturesImageProcessor {
    
    std::vector<uint8_t> BrightenImage(const std::vector<uint8_t>& pngData,
        const std::shared_ptr<bool>& brightnessEnabled) {
        // If brightness adjustment is explicitly disabled, we still need to ensure
        // the returned data is PNG. Decode whatever
        // image format was provided and re-encode to PNG without modifying pixels.
        if (brightnessEnabled && (!*brightnessEnabled)) {
            RLProfilePicturesLogger::LogInfo("Brightness adjustment is disabled, decoding and re-encoding to PNG");

            int width, height, channels_in_file;
            // request 0 to keep original channels
            unsigned char* rawData = stbi_load_from_memory(
                pngData.data(),
                static_cast<int>(pngData.size()),
                &width, &height, &channels_in_file, 0
            );

            if (!rawData) {
                RLProfilePicturesLogger::LogError("Failed to decode image data when brightness disabled");
                throw std::runtime_error("Failed to decode image data");
            }

            std::unique_ptr<unsigned char, decltype(&stbi_image_free)> decompressedData(rawData, stbi_image_free);

            // Determine channels to write (prefer 4 for RGBA if available, otherwise use channels_in_file)
            int out_channels = channels_in_file >= 4 ? 4 : channels_in_file;
            if (out_channels == 0) out_channels = 3; // fallback

            // If decoded channels != out_channels, convert by reloading with desired component count
            if (channels_in_file != out_channels) {
                // free previous and request desired channels
                decompressedData.reset();
                unsigned char* converted = stbi_load_from_memory(
                    pngData.data(),
                    static_cast<int>(pngData.size()),
                    &width, &height, &channels_in_file, out_channels
                );
                if (!converted) {
                    RLProfilePicturesLogger::LogError("Failed to convert decoded image to desired channels");
                    throw std::runtime_error("Failed to convert decoded image");
                }
                decompressedData.reset(converted);
            }

            // Re-encode to PNG
            std::vector<uint8_t> recompressedData;
            auto writeCallback = [](void* context, void* data, int size) {
                auto* vec = static_cast<std::vector<uint8_t>*>(context);
                vec->insert(vec->end(), reinterpret_cast<uint8_t*>(data), reinterpret_cast<uint8_t*>(data) + size);
            };

            int stride = width * out_channels;
            int success = stbi_write_png_to_func(writeCallback, &recompressedData, width, height,
                                               out_channels, decompressedData.get(), stride);

            if (!success) {
                RLProfilePicturesLogger::LogError("Failed to recompress PNG data when brightness disabled");
                throw std::runtime_error("Failed to recompress PNG data");
            }

            RLProfilePicturesLogger::LogSuccess("PNG recompressed successfully (brightness disabled), size: " +
                                               std::to_string(recompressedData.size()) + " bytes");
            return recompressedData;
        }

        RLProfilePicturesLogger::LogDebug("Starting BrightenImage");

        // Decompress PNG data using stb_image
        int width, height, channels;
        unsigned char* rawData = stbi_load_from_memory(
            pngData.data(),
            static_cast<int>(pngData.size()),
            &width, &height, &channels, 0
        );

        if (!rawData) {
            RLProfilePicturesLogger::LogError("Failed to decompress PNG data");
            throw std::runtime_error("Failed to decompress PNG data");
        }

        RLProfilePicturesLogger::LogSuccess("PNG decompressed successfully");
        RLProfilePicturesLogger::LogDebug("Image dimensions: " + std::to_string(width) + "x" + 
                                         std::to_string(height) + ", channels: " + std::to_string(channels));

        // Use smart pointer for automatic cleanup
        std::unique_ptr<unsigned char, decltype(&stbi_image_free)> decompressedData(rawData, stbi_image_free);

        int totalPixels = width * height * channels;
        RLProfilePicturesLogger::LogDebug("Total pixels: " + std::to_string(totalPixels));

        // Initialize sRGB lookup table (static for performance)
        static uint8_t srgb_lookup[256];
        static bool lookup_initialized = false;

        if (!lookup_initialized) {
            RLProfilePicturesLogger::LogDebug("Initializing sRGB lookup table");
            for (int i = 0; i < 256; i++) {
                srgb_lookup[i] = (uint8_t)(powf((float)i / 255.0f, 
                                               RLProfilePicturesConstants::GAMMA_CORRECTION_EXPONENT) * 255.0f);
            }
            lookup_initialized = true;
            RLProfilePicturesLogger::LogSuccess("sRGB lookup table initialized");
        }

        // Apply sRGB gamma correction to RGB channels only (preserve alpha)
        RLProfilePicturesLogger::LogDebug("Applying sRGB gamma correction to pixels");
        for (int i = 0; i < totalPixels / channels; i++) {
            for (int c = 0; c < channels; c++) {
                if (c < 3) { // Only apply to R, G, B channels
                    int pixelIndex = i * channels + c;
                    decompressedData.get()[pixelIndex] = srgb_lookup[decompressedData.get()[pixelIndex]];
                }
            }
        }
        RLProfilePicturesLogger::LogSuccess("Gamma correction applied");

        // Recompress to PNG format
        std::vector<uint8_t> recompressedData;
        auto writeCallback = [](void* context, void* data, int size) {
            auto* vec = static_cast<std::vector<uint8_t>*>(context);
            vec->insert(vec->end(), reinterpret_cast<uint8_t*>(data), reinterpret_cast<uint8_t*>(data) + size);
        };

        int success = stbi_write_png_to_func(writeCallback, &recompressedData, width, height,
                                           channels, decompressedData.get(), width * channels);

        if (!success) {
            RLProfilePicturesLogger::LogError("Failed to recompress PNG data");
            throw std::runtime_error("Failed to recompress PNG data");
        }

        RLProfilePicturesLogger::LogSuccess("PNG recompressed successfully, size: " + 
                                           std::to_string(recompressedData.size()) + " bytes");
        return recompressedData;
    }
}
