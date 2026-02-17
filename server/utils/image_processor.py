import io
import logging
import asyncio
from PIL import Image, ImageFilter
from typing import Optional, Tuple
import aiofiles
import httpx
from utils.http_client import HttpClient

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self, target_size: Tuple[int, int] = (32, 32), quality: int = 95):
        self.target_size = target_size
        self.quality = quality
    
    async def download_and_process_image(self, url: str) -> Optional[bytes]:
        """Download an image from URL and process it to target size."""
        try:
            client = await HttpClient.get_client()
            response = await client.get(url, timeout=20.0)
            if response.status_code == 200:
                return await self.process_image_bytes(response.content)
            else:
                logger.warning(f"Failed to download image from {url}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return None
    
    async def process_image_bytes(self, image_bytes: bytes) -> Optional[bytes]:
        """Process image bytes to PNG with high quality, accepting multiple input formats."""
        # Offload synchronous, CPU-bound PIL work to a thread to avoid blocking the event loop
        try:
            return await asyncio.to_thread(self._process_image_bytes_sync, image_bytes)
        except Exception as e:
            logger.exception(f"Error processing image in thread: {e}")
            return None

    def _process_image_bytes_sync(self, image_bytes: bytes) -> Optional[bytes]:
        """Synchronous helper for processing image bytes. Intended to run in a thread."""
        try:
            # Open from bytes
            with Image.open(io.BytesIO(image_bytes)) as image:
                image_format = image.format  # e.g., JPEG, WEBP, PNG, TIFF, GIF
                logger.debug(f"[sync] Loaded input image format: {image_format}, mode: {image.mode}")

                # Handle animated formats (GIF, WEBP): take first frame
                if getattr(image, "is_animated", False):
                    image.seek(0)
                    # Convert animated image to static
                    image = image.copy()

                # Normalize mode (PNG requires either RGB or RGBA)
                if image.mode not in ("RGB", "RGBA"):
                    if image.mode in ("L", "LA"):  # grayscale
                        image = image.convert("RGBA" if "A" in image.mode else "RGB")
                    elif image.mode == "P":  # palette-based
                        image = image.convert("RGBA" if "transparency" in image.info else "RGB")
                    else:
                        image = image.convert("RGBA")

                # Resize with your high-quality function
                processed_image = self.resize_high_quality(image, self.target_size)

                # Always save as PNG with proper compression
                output = io.BytesIO()
                processed_image.save(
                    output,
                    format="PNG",
                    compress_level=6,  # Good balance of size vs speed (0-9)
                    optimize=True,
                )
                return output.getvalue()

        except Exception as e:
            logger.exception(f"[sync] Error processing image: {e}")
            return None
    
    def resize_high_quality(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Resize image with high quality algorithms."""
        original_size = image.size
        
        # If already the right size, return as is
        if original_size == target_size:
            return image
        
        # For upscaling, use LANCZOS for better quality
        # For downscaling, use a combination of techniques
        if original_size[0] < target_size[0] or original_size[1] < target_size[1]:
            # Upscaling
            resized = image.resize(target_size, Image.Resampling.LANCZOS)
        else:
            # Downscaling - use a two-step process for better quality
            # First, resize to 2x the target size if possible
            intermediate_size = (target_size[0] * 2, target_size[1] * 2)
            if original_size[0] > intermediate_size[0] and original_size[1] > intermediate_size[1]:
                intermediate = image.resize(intermediate_size, Image.Resampling.LANCZOS)
                # Apply slight sharpening
                intermediate = intermediate.filter(ImageFilter.UnsharpMask(radius=0.5, percent=150, threshold=3))
                # Final resize
                resized = intermediate.resize(target_size, Image.Resampling.LANCZOS)
            else:
                resized = image.resize(target_size, Image.Resampling.LANCZOS)
        
        return resized
    
    async def save_processed_image(self, image_bytes: bytes, file_path: str) -> bool:
        """Save processed image bytes to file."""
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(image_bytes)
            return True
        except Exception as e:
            logger.error(f"Error saving image to {file_path}: {e}")
            return False



