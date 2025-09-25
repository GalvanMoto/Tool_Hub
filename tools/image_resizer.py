"""
Image resizer functionality for ToolHub.
Provides tools to resize images while maintaining quality and aspect ratio.
"""

import os
import tempfile
from typing import Tuple, Optional
from PIL import Image, ImageOps
import io
import base64


class ImageResizer:
    """Handles image resizing operations with quality preservation."""
    
    def __init__(self):
        """Initialize image resizer."""
        self.supported_formats = {
            'JPEG': ['.jpg', '.jpeg'],
            'PNG': ['.png'],
            'WEBP': ['.webp'],
            'BMP': ['.bmp'],
            'TIFF': ['.tiff', '.tif'],
            'GIF': ['.gif']
        }
    
    def resize_image(self, 
                    image_path: str, 
                    width: Optional[int] = None,
                    height: Optional[int] = None,
                    percentage: Optional[float] = None,
                    maintain_aspect: bool = True,
                    quality: int = 95,
                    output_format: Optional[str] = None,
                    output_filename: Optional[str] = None) -> str:
        """
        Resize an image with various options.
        
        Args:
            image_path: Path to the input image
            width: Target width in pixels
            height: Target height in pixels
            percentage: Resize by percentage (0-500)
            maintain_aspect: Whether to maintain aspect ratio
            quality: JPEG quality (1-100)
            output_format: Output format (JPEG, PNG, etc.)
            output_filename: Optional output filename
            
        Returns:
            Path to the resized image
            
        Raises:
            ValueError: If invalid parameters provided
            FileNotFoundError: If input image doesn't exist
            Exception: If resizing fails
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Validate resize parameters
        if not any([width, height, percentage]):
            raise ValueError("Must specify width, height, or percentage")
        
        if percentage and (percentage <= 0 or percentage > 500):
            raise ValueError("Percentage must be between 1 and 500")
        
        if quality < 1 or quality > 100:
            raise ValueError("Quality must be between 1 and 100")
        
        try:
            # Open and process image
            with Image.open(image_path) as img:
                # Auto-rotate based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Get original dimensions
                orig_width, orig_height = img.size
                
                # Calculate new dimensions
                if percentage:
                    new_width = int(orig_width * percentage / 100)
                    new_height = int(orig_height * percentage / 100)
                elif width and height:
                    if maintain_aspect:
                        # Calculate aspect ratio preserving dimensions
                        aspect_ratio = orig_width / orig_height
                        if width / height > aspect_ratio:
                            width = int(height * aspect_ratio)
                        else:
                            height = int(width / aspect_ratio)
                    new_width, new_height = width, height
                elif width:
                    aspect_ratio = orig_width / orig_height
                    new_width = width
                    new_height = int(width / aspect_ratio)
                else:  # height only
                    aspect_ratio = orig_width / orig_height
                    new_height = height
                    new_width = int(height * aspect_ratio)
                
                # Ensure minimum size
                new_width = max(1, new_width)
                new_height = max(1, new_height)
                
                # Resize image using high-quality resampling
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Determine output format
                if output_format:
                    save_format = output_format.upper()
                else:
                    save_format = img.format or 'JPEG'
                
                # Generate output path
                if output_filename is None:
                    output_fd, output_path = tempfile.mkstemp(
                        suffix=f'.{save_format.lower()}', 
                        prefix='resized_'
                    )
                    os.close(output_fd)
                else:
                    output_path = output_filename
                
                # Save resized image
                save_kwargs = {}
                if save_format == 'JPEG':
                    save_kwargs = {
                        'quality': quality,
                        'optimize': True,
                        'progressive': True
                    }
                elif save_format == 'PNG':
                    save_kwargs = {
                        'optimize': True
                    }
                elif save_format == 'WEBP':
                    save_kwargs = {
                        'quality': quality,
                        'optimize': True
                    }
                
                resized_img.save(output_path, format=save_format, **save_kwargs)
                
                return output_path
                
        except Exception as e:
            raise Exception(f"Failed to resize image: {str(e)}")
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Get comprehensive information about an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with image information
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError("Image file not found")
            
            with Image.open(image_path) as img:
                # Auto-rotate to get correct dimensions
                img = ImageOps.exif_transpose(img)
                
                # Get file size
                file_size = os.path.getsize(image_path)
                
                # Calculate megapixels
                width, height = img.size
                megapixels = (width * height) / 1_000_000
                
                return {
                    'file_path': image_path,
                    'file_size': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'file_size_kb': round(file_size / 1024, 2),
                    'format': img.format,
                    'mode': img.mode,
                    'width': width,
                    'height': height,
                    'megapixels': round(megapixels, 2),
                    'aspect_ratio': round(width / height, 3),
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'valid': True
                }
                
        except Exception as e:
            return {
                'file_path': image_path,
                'error': str(e),
                'valid': False
            }
    
    def validate_image_file(self, file_path: str) -> bool:
        """
        Validate if a file is a supported image format.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file is a valid image, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            # Check file extension
            ext = os.path.splitext(file_path)[1].lower()
            valid_extensions = []
            for format_exts in self.supported_formats.values():
                valid_extensions.extend(format_exts)
            
            if ext not in valid_extensions:
                return False
            
            # Try to open with PIL
            with Image.open(file_path) as img:
                img.verify()  # Verify it's a valid image
                return True
                
        except Exception:
            return False
    
    def get_resize_preview(self, 
                          original_width: int, 
                          original_height: int,
                          width: Optional[int] = None,
                          height: Optional[int] = None,
                          percentage: Optional[float] = None,
                          maintain_aspect: bool = True) -> dict:
        """
        Calculate what the new dimensions would be without actually resizing.
        
        Args:
            original_width: Original image width
            original_height: Original image height
            width: Target width
            height: Target height
            percentage: Resize percentage
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Dictionary with preview information
        """
        try:
            if percentage:
                new_width = int(original_width * percentage / 100)
                new_height = int(original_height * percentage / 100)
            elif width and height:
                if maintain_aspect:
                    aspect_ratio = original_width / original_height
                    if width / height > aspect_ratio:
                        width = int(height * aspect_ratio)
                    else:
                        height = int(width / aspect_ratio)
                new_width, new_height = width, height
            elif width:
                aspect_ratio = original_width / original_height
                new_width = width
                new_height = int(width / aspect_ratio)
            else:  # height only
                aspect_ratio = original_width / original_height
                new_height = height
                new_width = int(height * aspect_ratio)
            
            # Calculate reduction/enlargement
            size_change = (new_width * new_height) / (original_width * original_height)
            percentage_change = size_change * 100
            
            return {
                'new_width': max(1, new_width),
                'new_height': max(1, new_height),
                'size_change_percentage': round(percentage_change, 1),
                'is_enlargement': size_change > 1,
                'aspect_ratio_maintained': maintain_aspect
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'valid': False
            }