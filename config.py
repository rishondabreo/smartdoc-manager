# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-here'
    BUCKET_NAME = os.environ.get('BUCKET_NAME') or 'stellar-sunrise-473213-g6'
    
    # AI Features configuration
    ENABLE_AI_PROCESSING = True
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    # Supported file types
    ALLOWED_EXTENSIONS = {
        'images': {'png', 'jpg', 'jpeg', 'gif', 'bmp'},
        'documents': {'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx'},
        'archives': {'zip', 'rar'}
    }