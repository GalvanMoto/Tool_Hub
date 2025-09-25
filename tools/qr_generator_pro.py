"""
Enhanced QR Code generator with Pro features.
Supports multiple QR types, colors, logos, dynamic QR codes, and analytics.
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json

# Try to import styled PIL features, but fall back gracefully
try:
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer
    STYLED_QR_AVAILABLE = True
except ImportError:
    STYLED_QR_AVAILABLE = False


def apply_colors_manually(img, fg_color, bg_color):
    """
    Apply colors manually to a QR code image when color fill is not available.
    
    Args:
        img: PIL Image object
        fg_color: Foreground color (hex format)
        bg_color: Background color (hex format)
    
    Returns:
        PIL Image with colors applied
    """
    # Convert to RGBA for color manipulation
    img = img.convert('RGBA')
    data = img.getdata()
    
    new_data = []
    for item in data:
        # If pixel is black (QR code), make it fg_color
        if item[0] < 128:  # Assuming dark pixels are QR code
            # Convert hex to RGB
            fg_rgb = tuple(int(fg_color[i:i+2], 16) for i in (1, 3, 5))
            new_data.append((*fg_rgb, 255))
        else:  # White background, make it bg_color
            bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
            new_data.append((*bg_rgb, 255))
    
    img.putdata(new_data)
    return img.convert('RGB')


def generate_qr_code(data, 
                     size=300, 
                     border=4, 
                     error_correction='M', 
                     fg_color='#000000', 
                     bg_color='#FFFFFF',
                     logo=None,
                     style='square',
                     logo_size_ratio=0.2):
    """
    Generate a QR code with customization options.
    
    Args:
        data: The data to encode in the QR code
        size: Size of the QR code in pixels
        border: Border size around the QR code
        error_correction: Error correction level (L, M, Q, H)
        fg_color: Foreground color (hex format)
        bg_color: Background color (hex format)
        logo: Logo image file or path
        style: QR code style ('square', 'rounded', 'circle')
        logo_size_ratio: Size of logo relative to QR code (0.1-0.3)
    
    Returns:
        tuple: (PIL Image object, base64 encoded string)
    """
    
    # Error correction mapping
    error_levels = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Auto-adjust version
        error_correction=error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
        box_size=10,
        border=border,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create QR code image with fallback for different library versions
    try:
        if STYLED_QR_AVAILABLE and style in ['rounded', 'circle'] and style != 'square':
            # Try to use styled QR codes if available
            style_drawers = {
                'rounded': RoundedModuleDrawer(),
                'circle': CircleModuleDrawer()
            }
            
            # Use styled image without color mask (apply colors later)
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=style_drawers.get(style),
                fill_color=fg_color,
                back_color=bg_color
            )
        else:
            # Fallback to basic QR code
            img = qr.make_image(fill_color=fg_color, back_color=bg_color)
    except Exception as e:
        print(f"Error creating styled QR code: {e}")
        # Final fallback to basic QR code
        img = qr.make_image(fill_color=fg_color, back_color=bg_color)
    
    # Resize to requested size
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Add logo if provided
    if logo:
        img = add_logo_to_qr(img, logo, logo_size_ratio)
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return img, img_base64


def add_logo_to_qr(qr_img, logo, size_ratio=0.2):
    """
    Add a logo to the center of a QR code.
    
    Args:
        qr_img: PIL Image of the QR code
        logo: Logo image file or PIL Image
        size_ratio: Size of logo relative to QR code
    
    Returns:
        PIL Image with logo added
    """
    try:
        # Open logo image
        if isinstance(logo, str):
            logo_img = Image.open(logo)
        else:
            logo_img = logo
        
        # Convert to RGBA if needed
        if logo_img.mode != 'RGBA':
            logo_img = logo_img.convert('RGBA')
        
        # Calculate logo size
        qr_width, qr_height = qr_img.size
        logo_size = int(min(qr_width, qr_height) * size_ratio)
        
        # Resize logo
        logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Create a white background for the logo area
        logo_bg = Image.new('RGBA', (logo_size + 20, logo_size + 20), (255, 255, 255, 255))
        logo_bg_pos = ((logo_bg.size[0] - logo_size) // 2, (logo_bg.size[1] - logo_size) // 2)
        logo_bg.paste(logo_img, logo_bg_pos, logo_img)
        
        # Paste logo onto QR code
        qr_img = qr_img.convert('RGBA')
        logo_pos = ((qr_width - logo_bg.size[0]) // 2, (qr_height - logo_bg.size[1]) // 2)
        qr_img.paste(logo_bg, logo_pos, logo_bg)
        
        return qr_img.convert('RGB')
    except Exception as e:
        print(f"Error adding logo: {e}")
        return qr_img


def format_wifi_qr(ssid, password, security='WPA', hidden=False):
    """
    Format WiFi credentials for QR code.
    
    Args:
        ssid: WiFi network name
        password: WiFi password
        security: Security type (WPA, WEP, nopass)
        hidden: Whether network is hidden
    
    Returns:
        Formatted WiFi QR string
    """
    hidden_str = 'true' if hidden else 'false'
    return f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden_str};;"


def format_vcard_qr(contact_data):
    """
    Format vCard contact information for QR code.
    
    Args:
        contact_data: Dictionary with contact information
    
    Returns:
        Formatted vCard QR string
    """
    vcard = "BEGIN:VCARD\nVERSION:3.0\n"
    
    if contact_data.get('name'):
        vcard += f"FN:{contact_data['name']}\n"
    
    if contact_data.get('phone'):
        vcard += f"TEL:{contact_data['phone']}\n"
    
    if contact_data.get('email'):
        vcard += f"EMAIL:{contact_data['email']}\n"
    
    if contact_data.get('organization'):
        vcard += f"ORG:{contact_data['organization']}\n"
    
    if contact_data.get('url'):
        vcard += f"URL:{contact_data['url']}\n"
    
    if contact_data.get('address'):
        vcard += f"ADR:;;{contact_data['address']}\n"
    
    vcard += "END:VCARD"
    return vcard


def format_social_qr(platform, username):
    """
    Format social media profile for QR code.
    
    Args:
        platform: Social media platform
        username: Username or profile ID
    
    Returns:
        Social media URL
    """
    social_urls = {
        'twitter': f"https://twitter.com/{username}",
        'instagram': f"https://instagram.com/{username}",
        'linkedin': f"https://linkedin.com/in/{username}",
        'facebook': f"https://facebook.com/{username}",
        'tiktok': f"https://tiktok.com/@{username}",
        'youtube': f"https://youtube.com/@{username}",
        'github': f"https://github.com/{username}",
        'discord': f"https://discord.gg/{username}",
        'telegram': f"https://t.me/{username}",
        'whatsapp': f"https://wa.me/{username}"
    }
    
    return social_urls.get(platform.lower(), f"https://{platform}.com/{username}")


def save_uploaded_logo(logo_file, upload_folder='static/uploads/logos'):
    """
    Save uploaded logo file and return the path.
    
    Args:
        logo_file: FileStorage object from Flask
        upload_folder: Directory to save logos
    
    Returns:
        str: Path to saved logo file
    """
    if not logo_file or logo_file.filename == '':
        return None
    
    # Create upload directory if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    
    # Secure filename
    filename = secure_filename(logo_file.filename)
    
    # Add timestamp to prevent overwrites
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    
    filepath = os.path.join(upload_folder, filename)
    logo_file.save(filepath)
    
    return filepath


def get_qr_size_options():
    """Get available QR code size options."""
    return {
        'Small (200px)': 200,
        'Medium (300px)': 300,
        'Large (500px)': 500,
        'Extra Large (800px)': 800,
        'Print Quality (1200px)': 1200,  # Pro feature
        'Poster Size (2000px)': 2000     # Pro feature
    }


def get_error_correction_options():
    """Get error correction level options."""
    return {
        'L': 'Low (~7% damage recovery)',
        'M': 'Medium (~15% damage recovery)',
        'Q': 'Quartile (~25% damage recovery)',
        'H': 'High (~30% damage recovery)'
    }


def get_social_platforms():
    """Get available social media platforms."""
    return [
        'twitter',
        'instagram', 
        'linkedin',
        'facebook',
        'tiktok',
        'youtube',
        'github',
        'discord',
        'telegram',
        'whatsapp'
    ]


def format_data_by_type(qr_type, form_data):
    """
    Format QR data based on the selected type.
    
    Args:
        qr_type: Type of QR code (url, wifi, vcard, etc.)
        form_data: Form data from the request
    
    Returns:
        Formatted data string for QR code generation
    """
    if qr_type == 'url':
        url = form_data.get('url', '').strip()
        # Ensure URL has protocol
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    elif qr_type == 'text':
        return form_data.get('text', '').strip()
    
    elif qr_type == 'wifi':
        ssid = form_data.get('wifi_ssid', '').strip()
        password = form_data.get('wifi_password', '').strip()
        security = form_data.get('wifi_security', 'WPA')
        
        # WiFi QR format: WIFI:T:WPA;S:NetworkName;P:Password;H:false;;
        wifi_string = f"WIFI:T:{security};S:{ssid};"
        if password:
            wifi_string += f"P:{password};"
        wifi_string += "H:false;;"
        return wifi_string
    
    elif qr_type == 'vcard':
        name = form_data.get('vcard_name', '').strip()
        company = form_data.get('vcard_company', '').strip()
        phone = form_data.get('vcard_phone', '').strip()
        email = form_data.get('vcard_email', '').strip()
        address = form_data.get('vcard_address', '').strip()
        
        # vCard format
        vcard = "BEGIN:VCARD\nVERSION:3.0\n"
        if name:
            vcard += f"FN:{name}\n"
        if company:
            vcard += f"ORG:{company}\n"
        if phone:
            vcard += f"TEL:{phone}\n"
        if email:
            vcard += f"EMAIL:{email}\n"
        if address:
            vcard += f"ADR:;;{address}\n"
        vcard += "END:VCARD"
        return vcard
    
    elif qr_type == 'email':
        to_email = form_data.get('email_to', '').strip()
        subject = form_data.get('email_subject', '').strip()
        body = form_data.get('email_body', '').strip()
        
        # mailto format
        email_string = f"mailto:{to_email}"
        params = []
        if subject:
            params.append(f"subject={subject}")
        if body:
            params.append(f"body={body}")
        
        if params:
            email_string += "?" + "&".join(params)
        return email_string
    
    elif qr_type == 'phone':
        phone_number = form_data.get('phone_number', '').strip()
        return f"tel:{phone_number}"
    
    elif qr_type == 'sms':
        number = form_data.get('sms_number', '').strip()
        message = form_data.get('sms_message', '').strip()
        
        sms_string = f"sms:{number}"
        if message:
            sms_string += f"?body={message}"
        return sms_string
    
    elif qr_type == 'whatsapp':
        number = form_data.get('whatsapp_number', '').strip()
        message = form_data.get('whatsapp_message', '').strip()
        
        # Remove + and any non-digits from phone number
        clean_number = ''.join(filter(str.isdigit, number))
        
        whatsapp_url = f"https://wa.me/{clean_number}"
        if message:
            whatsapp_url += f"?text={message}"
        return whatsapp_url
    
    elif qr_type == 'social':
        platform = form_data.get('social_platform', 'instagram')
        username = form_data.get('social_username', '').strip()
        
        # If it's already a URL, use it as is
        if username.startswith('http'):
            return username
        
        # Generate platform URLs
        platform_urls = {
            'instagram': f"https://instagram.com/{username}",
            'facebook': f"https://facebook.com/{username}",
            'twitter': f"https://twitter.com/{username}",
            'tiktok': f"https://tiktok.com/@{username}",
            'linkedin': f"https://linkedin.com/in/{username}",
            'snapchat': f"https://snapchat.com/add/{username}"
        }
        return platform_urls.get(platform, f"https://{platform}.com/{username}")
    
    elif qr_type == 'youtube':
        youtube_url = form_data.get('youtube_url', '').strip()
        return youtube_url
    
    elif qr_type == 'location':
        location_type = form_data.get('location_type', 'coordinates')
        
        if location_type == 'coordinates':
            lat = form_data.get('latitude', '').strip()
            lng = form_data.get('longitude', '').strip()
            return f"geo:{lat},{lng}"
        
        elif location_type == 'address':
            address = form_data.get('address', '').strip()
            return f"geo:0,0?q={address}"
        
        elif location_type == 'google_maps':
            maps_url = form_data.get('maps_url', '').strip()
            return maps_url
    
    elif qr_type == 'file':
        # File upload is handled in the route, this should not be called for file type
        # Return a placeholder that indicates file upload is needed
        return "FILE_UPLOAD_REQUIRED"
    
    elif qr_type == 'upi':
        upi_id = form_data.get('upi_id', '').strip()
        payee_name = form_data.get('payee_name', '').strip()
        amount = form_data.get('amount', '').strip()
        transaction_note = form_data.get('transaction_note', '').strip()
        currency = form_data.get('currency', 'INR')
        
        # UPI Payment URL format
        upi_url = f"upi://pay?pa={upi_id}&pn={payee_name}"
        if amount:
            upi_url += f"&am={amount}"
        if transaction_note:
            upi_url += f"&tn={transaction_note}"
        upi_url += f"&cu={currency}"
        return upi_url
    
    elif qr_type == 'paypal':
        paypal_email = form_data.get('paypal_email', '').strip()
        paypal_type = form_data.get('paypal_type', 'donate')
        amount = form_data.get('paypal_amount', '').strip()
        currency = form_data.get('paypal_currency', 'USD')
        item_name = form_data.get('item_name', '').strip()
        
        # PayPal payment URL format
        paypal_url = f"https://www.paypal.com/cgi-bin/webscr?cmd=_{'donations' if paypal_type == 'donate' else 'xclick'}&business={paypal_email}"
        if amount:
            paypal_url += f"&amount={amount}"
        if currency:
            paypal_url += f"&currency_code={currency}"
        if item_name:
            paypal_url += f"&item_name={item_name}"
        if paypal_type == 'donate' and item_name:
            paypal_url += f"&item_number=1"
        return paypal_url
    
    elif qr_type == 'crypto':
        crypto_type = form_data.get('crypto_type', 'bitcoin')
        crypto_address = form_data.get('crypto_address', '').strip()
        amount = form_data.get('crypto_amount', '').strip()
        label = form_data.get('crypto_label', '').strip()
        message = form_data.get('crypto_message', '').strip()
        
        # Cryptocurrency URI format
        crypto_schemes = {
            'bitcoin': 'bitcoin',
            'ethereum': 'ethereum',
            'litecoin': 'litecoin',
            'dogecoin': 'dogecoin',
            'binance': 'binancecoin'
        }
        
        scheme = crypto_schemes.get(crypto_type, crypto_type)
        crypto_uri = f"{scheme}:{crypto_address}"
        
        params = []
        if amount:
            params.append(f"amount={amount}")
        if label:
            params.append(f"label={label}")
        if message:
            params.append(f"message={message}")
        
        if params:
            crypto_uri += "?" + "&".join(params)
        
        return crypto_uri
    
    else:
        # Default to URL type
        return form_data.get('url', form_data.get('data', ''))


def validate_qr_data(qr_type, form_data):
    """
    Validate QR data based on type and return formatted data.
    
    Args:
        qr_type: Type of QR code
        form_data: Form data from request
    
    Returns:
        Tuple: (is_valid, error_message, formatted_data)
    """
    try:
        formatted_data = format_data_by_type(qr_type, form_data)
        
        if not formatted_data or formatted_data.strip() == '':
            return False, "Please provide the required data for this QR type", None
        
        # Type-specific validation
        if qr_type == 'url':
            url = form_data.get('url', '').strip()
            if not url:
                return False, "URL is required", None
            if len(url) > 2000:
                return False, "URL is too long (max 2000 characters)", None
        
        elif qr_type == 'wifi':
            ssid = form_data.get('wifi_ssid', '').strip()
            if not ssid:
                return False, "WiFi network name (SSID) is required", None
        
        elif qr_type == 'vcard':
            name = form_data.get('vcard_name', '').strip()
            if not name:
                return False, "Name is required for vCard", None
        
        elif qr_type == 'email':
            email = form_data.get('email_to', '').strip()
            if not email:
                return False, "Email address is required", None
            if '@' not in email:
                return False, "Invalid email address", None
        
        elif qr_type in ['phone', 'sms']:
            number_field = 'phone_number' if qr_type == 'phone' else 'sms_number'
            number = form_data.get(number_field, '').strip()
            if not number:
                return False, "Phone number is required", None
        
        elif qr_type == 'whatsapp':
            number = form_data.get('whatsapp_number', '').strip()
            if not number:
                return False, "WhatsApp number is required", None
        
        elif qr_type == 'social':
            username = form_data.get('social_username', '').strip()
            if not username:
                return False, "Username or profile URL is required", None
        
        elif qr_type == 'youtube':
            url = form_data.get('youtube_url', '').strip()
            if not url:
                return False, "YouTube URL is required", None
            if 'youtube.com' not in url and 'youtu.be' not in url:
                return False, "Please enter a valid YouTube URL", None
        
        elif qr_type == 'location':
            location_type = form_data.get('location_type', 'coordinates')
            if location_type == 'coordinates':
                lat = form_data.get('latitude', '').strip()
                lng = form_data.get('longitude', '').strip()
                if not lat or not lng:
                    return False, "Both latitude and longitude are required", None
            elif location_type == 'address':
                address = form_data.get('address', '').strip()
                if not address:
                    return False, "Address is required", None
            elif location_type == 'google_maps':
                maps_url = form_data.get('maps_url', '').strip()
                if not maps_url:
                    return False, "Google Maps URL is required", None
        
        elif qr_type == 'file':
            # File upload validation is handled in the route
            # This function should not be called for file type normally
            if formatted_data == "FILE_UPLOAD_REQUIRED":
                return False, "Please select a file to upload", None
        
        elif qr_type == 'upi':
            upi_id = form_data.get('upi_id', '').strip()
            payee_name = form_data.get('payee_name', '').strip()
            if not upi_id:
                return False, "UPI ID is required", None
            if not payee_name:
                return False, "Payee name is required", None
            if '@' not in upi_id:
                return False, "Invalid UPI ID format", None
        
        elif qr_type == 'paypal':
            paypal_email = form_data.get('paypal_email', '').strip()
            if not paypal_email:
                return False, "PayPal email is required", None
            if '@' not in paypal_email:
                return False, "Invalid PayPal email format", None
        
        elif qr_type == 'crypto':
            crypto_address = form_data.get('crypto_address', '').strip()
            if not crypto_address:
                return False, "Cryptocurrency wallet address is required", None
            if len(crypto_address) < 10:
                return False, "Invalid cryptocurrency address", None
        
        # Check data length (QR codes have limits)
        if len(formatted_data) > 4000:
            return False, "Data is too long for QR code (max 4000 characters)", None
        
        return True, None, formatted_data
        
    except Exception as e:
        return False, f"Error processing data: {str(e)}", None


# Legacy class for backward compatibility
class QRCodeGenerator:
    """Legacy QR code generator class for backward compatibility."""
    
    def __init__(self):
        pass
    
    def generate_qr_code(self, data, size=300, error_correction='M', fill_color='black', back_color='white'):
        """Legacy method - redirects to new function."""
        try:
            img, img_base64 = generate_qr_code(
                data=data,
                size=size,
                error_correction=error_correction,
                fg_color=fill_color,
                bg_color=back_color
            )
            return img_base64
        except Exception as e:
            return f"Error: {str(e)}"
    
    def validate_data(self, data):
        """Legacy validation method."""
        if not data or len(data.strip()) == 0:
            return False, "Data cannot be empty"
        if len(data) > 4000:
            return False, "Data is too long for QR code"
        return True, None
    
    def detect_data_type(self, data):
        """Legacy method to detect data type."""
        if data.startswith(('http://', 'https://')):
            return "URL"
        elif data.startswith('mailto:'):
            return "Email"
        elif data.startswith('tel:'):
            return "Phone"
        elif '@' in data and '.' in data:
            return "Email"
        else:
            return "Text"