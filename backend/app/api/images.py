"""
Image Proxy API - Serves product images from local storage and Picsum fallback
"""

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
import io
from pathlib import Path
import os

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/local/{filename}")
async def serve_local_image(filename: str):
    """
    Serve images directly from local_images directory
    """
    try:
        # Construct path to local image
        image_path = Path(f"/Users/vijaygk/Documents/spm/zyra-vision-shop/backend/local_images/{filename}")
        
        if image_path.exists() and image_path.is_file():
            # Determine media type based on file extension
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                media_type = "image/jpeg"
            elif filename.lower().endswith('.png'):
                media_type = "image/png"
            elif filename.lower().endswith('.webp'):
                media_type = "image/webp"
            else:
                media_type = "image/jpeg"  # Default
            
            return FileResponse(
                path=str(image_path),
                media_type=media_type,
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Content-Disposition": f"inline; filename={filename}"
                }
            )
        else:
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image serving error: {str(e)}")


@router.get("/products/{product_id}/{filename}")
async def serve_product_image(product_id: str, filename: str):
    """
    Serve product images from local storage (legacy endpoint)
    """
    try:
        # Construct path to product image
        image_path = Path(f"/Users/vijaygk/Documents/spm/zyra-vision-shop/backend/uploads/products/{product_id}/{filename}")
        
        if image_path.exists() and image_path.is_file():
            # Determine media type based on file extension
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                media_type = "image/jpeg"
            elif filename.lower().endswith('.png'):
                media_type = "image/png"
            elif filename.lower().endswith('.webp'):
                media_type = "image/webp"
            else:
                media_type = "image/jpeg"  # Default
            
            return FileResponse(
                path=str(image_path),
                media_type=media_type,
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Content-Disposition": f"inline; filename={filename}"
                }
            )
        else:
            # Fallback to Picsum if image doesn't exist
            return await proxy_image_fallback(product_id, filename)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image serving error: {str(e)}")


@router.get("/proxy/{product_id}/{image_num}")
async def proxy_image(product_id: str, image_num: int):
    """
    Fetch random images from Picsum based on product ID
    This creates consistent random images using Picsum with deterministic seeds
    """
    try:
        # Create deterministic seed for consistent images
        import hashlib
        import time
        seed = hashlib.md5(f"{product_id}_{image_num}".encode()).hexdigest()[:8]
        
        # Use standard dimensions
        width, height = 400, 400
        
        # Add cache-busting parameter for development
        cache_buster = int(time.time() / 60)  # Changes every minute for development
        
        # Generate headers with cache-busting for development
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",  # Disable caching for development
            "Pragma": "no-cache",
            "Expires": "0",
            "Content-Disposition": f"inline; filename={product_id}_{image_num}.jpg",
            "ETag": f'"{seed}_{width}_{height}_{cache_buster}"'  # Add cache buster to ETag
        }
        
        # Fetch image from Picsum with deterministic seed
        picsum_url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
        picsum_url += f"?cb={cache_buster}"
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(picsum_url, timeout=10.0)
            response.raise_for_status()
            
            return StreamingResponse(
                io.BytesIO(response.content),
                media_type="image/jpeg",
                headers=headers
            )
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch image from Picsum: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image proxy error: {str(e)}")


@router.get("/placeholder/{width}/{height}")
async def placeholder_image(width: int, height: int):
    """
    Generate a simple placeholder image
    """
    try:
        # Create a simple placeholder using Picsum
        picsum_url = f"https://picsum.photos/{width}/{height}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(picsum_url, timeout=10.0)
            response.raise_for_status()
            
            return StreamingResponse(
                io.BytesIO(response.content),
                media_type="image/jpeg",
                headers={
                    "Cache-Control": "public, max-age=3600"
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Placeholder error: {str(e)}")


async def proxy_image_fallback(product_id: str, filename: str):
    """
    Fallback to Picsum when local image doesn't exist
    """
    try:
        # Create deterministic seed for consistent images
        import hashlib
        import time
        seed = hashlib.md5(f"{product_id}_{filename}".encode()).hexdigest()[:8]
        
        # Use standard dimensions
        width, height = 400, 400
        
        # Add cache-busting parameter for development
        cache_buster = int(time.time() / 60)  # Changes every minute for development
        
        # Fetch image from Picsum with deterministic seed
        picsum_url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
        picsum_url += f"?cb={cache_buster}"
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(picsum_url, timeout=10.0)
            response.raise_for_status()
            
            return StreamingResponse(
                io.BytesIO(response.content),
                media_type="image/jpeg",
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Content-Disposition": f"inline; filename={filename}"
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallback image error: {str(e)}")
