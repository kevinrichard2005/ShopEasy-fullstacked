import os

class Config:
    """Application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'shopeasy-secret-key-2024-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///shopeasy_v2.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Razorpay Configuration (Test Mode)
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_XXXXXXXXXXXXXXX')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'XXXXXXXXXXXXXXXXXXXXXXXX')
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
