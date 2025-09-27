# utils/file_validator.py
from config import Config
import os

class FileValidator:
    def __init__(self):
        self.config = Config()
    
    def validate_file(self, file):
        """Validate file size and type"""
        result = {'valid': True, 'message': ''}
        
        # Check file size
        file.seek(0, 2)  # Seek to end to get size
        file_size = file.tell()
        file.seek(0)  # Reset seek position
        
        if file_size > self.config.MAX_FILE_SIZE:
            result['valid'] = False
            result['message'] = f'File too large. Maximum size is {self.config.MAX_FILE_SIZE // (1024*1024)}MB'
            return result
        
        # Check file extension
        if file.filename:
            filename = file.filename.lower()
            file_extension = filename.rsplit('.', 1)[1] if '.' in filename else ''
            
            allowed_extensions = set()
            for category in self.config.ALLOWED_EXTENSIONS.values():
                allowed_extensions.update(category)
            
            if file_extension not in allowed_extensions:
                result['valid'] = False
                result['message'] = f'File type {file_extension} not allowed. Allowed types: {", ".join(allowed_extensions)}'
        
        return result