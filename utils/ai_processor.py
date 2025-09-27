# utils/ai_processor.py
from google.cloud import vision
import io

class AIProcessor:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
    
    def extract_text_from_image(self, file_content):
        """Extract text from images using Google Vision OCR"""
        try:
            image = vision.Image(content=file_content)
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                return texts[0].description
            return "No text found"
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def analyze_document_properties(self, file_content, file_type):
        """Analyze document properties"""
        analysis = {
            'file_type': file_type,
            'has_text': False,
            'text_content': '',
            'word_count': 0,
            'analysis_time': None
        }
        
        import time
        start_time = time.time()
        
        try:
            if file_type in ['png', 'jpg', 'jpeg']:
                text = self.extract_text_from_image(file_content)
                analysis['text_content'] = text
                analysis['has_text'] = bool(text.strip())
                analysis['word_count'] = len(text.split())
            
            elif file_type == 'pdf':
                analysis['text_content'] = "PDF text extraction would go here"
                analysis['has_text'] = True
            
            analysis['analysis_time'] = round(time.time() - start_time, 2)
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis