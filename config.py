import os
from datetime import timedelta

class Config:
    DB_NAME = 'plastech'
    DB_PATH = os.path.join(os.getcwd(), DB_NAME)
    APP_NAME = "PlasTech"
    APP_ICON = "♻️"
    PAGE_TITLE = "PlasTech - Smart Waste Management"
    
    POINTS_MAP = {   
        'default': 5
    }
    
    DETECTION_EXPIRY_HOURS = 24
    DETECTION_CONFIDENCE_THRESHOLD = 0.6  # 60% confidence
    
    # Path model
    YOLO_MODEL_PATH = os.path.join(os.getcwd(), 'waste_detection.pt')
    
    PRIMARY_COLOR = "#2E7D32"
    SECONDARY_COLOR = "#4CAF50"
    
    @classmethod
    def get_expiry_timedelta(cls):
        return timedelta(hours=cls.DETECTION_EXPIRY_HOURS)