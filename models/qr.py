"""
QR Code models for dynamic QR codes, analytics, and user management.
"""

from models import db
from datetime import datetime
import string
import random


class QRCode(db.Model):
    """Model for storing QR code information and dynamic redirects."""
    
    __tablename__ = 'qr_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    qr_id = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Short ID for URLs
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for anonymous
    
    # QR Content
    qr_type = db.Column(db.String(20), nullable=False, default='url')  # url, wifi, vcard, social
    original_data = db.Column(db.Text, nullable=False)  # Original data encoded
    current_data = db.Column(db.Text, nullable=False)  # Current redirect target (for dynamic)
    
    # QR Settings
    is_dynamic = db.Column(db.Boolean, default=False, nullable=False)
    size = db.Column(db.Integer, default=300, nullable=False)
    error_correction = db.Column(db.String(1), default='M', nullable=False)
    fg_color = db.Column(db.String(7), default='#000000', nullable=False)
    bg_color = db.Column(db.String(7), default='#FFFFFF', nullable=False)
    has_logo = db.Column(db.Boolean, default=False, nullable=False)
    logo_path = db.Column(db.String(255), nullable=True)
    
    # Status & Analytics
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    scan_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # Optional expiration
    
    # Relationships
    scans = db.relationship('QRScan', backref='qr_code', lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', backref='qr_codes')
    
    @staticmethod
    def generate_qr_id():
        """Generate a unique short QR ID."""
        chars = string.ascii_letters + string.digits
        while True:
            qr_id = ''.join(random.choices(chars, k=8))
            if not QRCode.query.filter_by(qr_id=qr_id).first():
                return qr_id
    
    def update_redirect(self, new_data):
        """Update the redirect target for dynamic QR codes."""
        if self.is_dynamic:
            self.current_data = new_data
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def increment_scan_count(self):
        """Increment scan count and save."""
        self.scan_count += 1
        db.session.commit()
    
    def get_redirect_url(self):
        """Get the current redirect URL for this QR code."""
        if self.is_dynamic:
            return self.current_data
        return self.original_data
    
    def to_dict(self):
        """Convert QR code to dictionary for API responses."""
        return {
            'id': self.id,
            'qr_id': self.qr_id,
            'qr_type': self.qr_type,
            'original_data': self.original_data,
            'current_data': self.current_data,
            'is_dynamic': self.is_dynamic,
            'is_active': self.is_active,
            'scan_count': self.scan_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def __repr__(self):
        return f'<QRCode {self.qr_id}>'


class QRScan(db.Model):
    """Model for tracking QR code scans and analytics."""
    
    __tablename__ = 'qr_scans'
    
    id = db.Column(db.Integer, primary_key=True)
    qr_code_id = db.Column(db.Integer, db.ForeignKey('qr_codes.id'), nullable=False)
    
    # Scan Information
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4/IPv6
    user_agent = db.Column(db.Text, nullable=True)
    referer = db.Column(db.String(255), nullable=True)
    
    # Geographic Data (can be populated from IP)
    country = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    
    # Device Information (parsed from user agent)
    device_type = db.Column(db.String(20), nullable=True)  # mobile, desktop, tablet
    browser = db.Column(db.String(50), nullable=True)
    os = db.Column(db.String(50), nullable=True)
    
    # Timing
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @staticmethod
    def create_scan(qr_code, request):
        """Create a new scan record from Flask request."""
        scan = QRScan(
            qr_code_id=qr_code.id,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent'),
            referer=request.headers.get('Referer')
        )
        
        # Parse device info from user agent (basic implementation)
        user_agent = request.headers.get('User-Agent', '').lower()
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            scan.device_type = 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            scan.device_type = 'tablet'
        else:
            scan.device_type = 'desktop'
        
        # Basic browser detection
        if 'chrome' in user_agent:
            scan.browser = 'Chrome'
        elif 'firefox' in user_agent:
            scan.browser = 'Firefox'
        elif 'safari' in user_agent:
            scan.browser = 'Safari'
        elif 'edge' in user_agent:
            scan.browser = 'Edge'
        
        # Basic OS detection
        if 'windows' in user_agent:
            scan.os = 'Windows'
        elif 'mac' in user_agent:
            scan.os = 'macOS'
        elif 'linux' in user_agent:
            scan.os = 'Linux'
        elif 'android' in user_agent:
            scan.os = 'Android'
        elif 'ios' in user_agent:
            scan.os = 'iOS'
        
        db.session.add(scan)
        db.session.commit()
        return scan
    
    def to_dict(self):
        """Convert scan to dictionary for API responses."""
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'scanned_at': self.scanned_at.isoformat()
        }
    
    def __repr__(self):
        return f'<QRScan {self.id} for QR {self.qr_code_id}>'


class QRTemplate(db.Model):
    """Model for storing QR code templates for different types."""
    
    __tablename__ = 'qr_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    qr_type = db.Column(db.String(20), nullable=False)
    template_data = db.Column(db.JSON, nullable=False)  # Template structure
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<QRTemplate {self.name}>'