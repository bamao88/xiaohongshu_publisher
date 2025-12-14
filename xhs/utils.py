import os
import httpx
from typing import List, Union
import re
import uuid
import asyncio


async def download_video(video_url: str, output_path: str = "output/video.mp4") -> bool:
    """Download video from URL to specified path."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(video_url, follow_redirects=True)
            response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(response.content)
                
        print(f"Video downloaded: {output_path}")
        return True
        
    except Exception as e:
        print(f"Download failed: {e}")
        return False


async def download_image(image_url: str, output_path: str) -> bool:
    """Download a single image from URL to specified path.

    Args:
        image_url: Image URL
        output_path: Local file path to save the image

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url, follow_redirects=True)
            response.raise_for_status()

            # Save the file first
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)

            # Verify it's a valid image by trying to open it
            try:
                from PIL import Image
                with Image.open(output_path) as img:
                    img.verify()  # Verify it's a valid image
                print(f"Image downloaded: {output_path}")
                return True
            except ImportError:
                # Pillow not installed, trust content-type header
                content_type = response.headers.get('content-type', '')
                if content_type.startswith('image/') or content_type == 'application/octet-stream':
                    print(f"Image downloaded: {output_path}")
                    return True
                print(f"URL may not be an image: {content_type}")
                return False
            except Exception as e:
                print(f"Downloaded file is not a valid image: {e}")
                os.remove(output_path)
                return False

    except Exception as e:
        print(f"Image download failed: {e}")
        return False


async def download_images(image_urls: List[str], output_dir: str = "output") -> List[str]:
    """Download multiple images concurrently.

    Args:
        image_urls: List of image URLs
        output_dir: Directory to save images

    Returns:
        List of successfully downloaded image paths
    """
    os.makedirs(output_dir, exist_ok=True)

    tasks = []
    image_paths = []

    for i, url in enumerate(image_urls):
        # Extract file extension from URL
        ext = url.split('.')[-1].split('?')[0] or 'jpg'
        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
            ext = 'jpg'

        output_path = os.path.join(output_dir, f"image_{i}_{uuid.uuid4().hex[:8]}.{ext}")
        image_paths.append(output_path)
        tasks.append(download_image(url, output_path))

    # Download all images concurrently
    results = await asyncio.gather(*tasks)

    # Return only successfully downloaded image paths
    successful_paths = [path for path, success in zip(image_paths, results) if success]
    print(f"Downloaded {len(successful_paths)}/{len(image_urls)} images")

    return successful_paths


def validate_image(image_path: str) -> bool:
    """Validate image format, size and dimensions.

    Args:
        image_path: Path to image file

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        from PIL import Image

        # Check if file exists
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return False

        # Check file size (< 10MB)
        file_size = os.path.getsize(image_path)
        if file_size > 10 * 1024 * 1024:
            print(f"Image too large: {file_size / 1024 / 1024:.2f}MB > 10MB")
            return False

        # Check image format and dimensions
        with Image.open(image_path) as img:
            # Check format
            if img.format.lower() not in ['jpeg', 'jpg', 'png', 'webp']:
                print(f"Unsupported image format: {img.format}")
                return False

            # Check dimensions (recommended >= 600x600)
            width, height = img.size
            if width < 600 or height < 600:
                print(f"Image dimensions too small: {width}x{height} (recommended >= 600x600)")
                # Not a hard failure, just a warning

        return True

    except ImportError:
        print("Warning: Pillow not installed, skipping image validation")
        return True  # Don't fail if Pillow is not installed
    except Exception as e:
        print(f"Image validation failed: {e}")
        return False


def parse_tags(tags: Union[str, List[str]]) -> List[str]:
    """Parse tags from string "#tag1 #tag2" or list ["tag1", "tag2"] format.

    Supports Chinese characters in tags.
    """
    if isinstance(tags, list):
        return [tag.lstrip('#') for tag in tags]

    if isinstance(tags, str):
        # Extract hashtags with Chinese support: #tag1 #标签2 -> ["tag1", "标签2"]
        matches = re.findall(r'#([\w\u4e00-\u9fff]+)', tags)
        if matches:
            return matches
        # Fallback: split by spaces
        return [tag.strip().lstrip('#') for tag in tags.split() if tag.strip()]

    return []