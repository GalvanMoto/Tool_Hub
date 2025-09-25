"""
QR Code generation functionality for ToolHub.
Provides tools to generate QR codes for various types of data.
"""

import qrcode
import io
import base64
from PIL import Image


class QRCodeGenerator:
    """Handles QR code generation operations."""
    
    def __init__(self):
        """Initialize QR code generator."""
        pass
    
    def generate_qr_code(self, data, size=300, error_correction='M', fill_color='black', back_color='white'):
        """
        Generate QR code for given data.
        
        Args:
            data: Data to encode in QR code
            size: Size of the QR code image (width/height in pixels)
            error_correction: Error correction level ('L', 'M', 'Q', 'H')
            fill_color: Color of QR code pattern
            back_color: Background color
            
        Returns:
            Base64 encoded PNG image string
        """
        # Map error correction levels
        error_levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H,
        }
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,  # Auto-determine version
            error_correction=error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=10,
            border=4,
        )
        
        # Add data and generate
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Resize to specified size
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
    
    def validate_data(self, data):
        """
        Validate input data for QR code generation.
        
        Args:
            data: Input data to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not data or not data.strip():
            return False, "Data cannot be empty"
        
        # Check data length (QR codes have limits)
        if len(data) > 2000:  # Conservative limit
            return False, "Data is too long (max 2000 characters)"
        
        return True, None
    
    def get_qr_info(self, data):
        """
        Get information about what would be generated for given data.
        
        Args:
            data: Input data
            
        Returns:
            Dictionary with QR code information
        """
        try:
            # Create temporary QR to get info
            qr = qrcode.QRCode()
            qr.add_data(data)
            qr.make(fit=True)
            
            return {
                'version': qr.version,
                'error_correction': qr.error_correction,
                'data_length': len(data),
                'estimated_size': f"{qr.modules_count}x{qr.modules_count} modules"
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def detect_data_type(self, data):
        """
        Detect the type of data being encoded.
        
        Args:
            data: Input data
            
        Returns:
            String describing the detected data type
        """
        data = data.strip()
        
        if data.startswith(('http://', 'https://')):
            return 'URL'
        elif data.startswith('mailto:'):
            return 'Email'
        elif data.startswith('tel:'):
            return 'Phone Number'
        elif data.startswith('geo:'):
            return 'GPS Coordinates'
        elif data.startswith('WIFI:'):
            return 'WiFi Configuration'
        elif '@' in data and '.' in data:
            return 'Email Address'
        elif data.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '').isdigit():
            return 'Phone Number'
        else:
            return 'Text'