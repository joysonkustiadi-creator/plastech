import os
import numpy as np
from config import Config
from PIL import Image

# Mapping kelas YOLO ke kategori PlasTech
CLASS_MAPPING = {
    # Bottles
    "Clear plastic bottle": "bottle",
    "Other plastic bottle": "bottle",
    "Glass bottle": "bottle",
    
    # Bottle Caps
    "Plastic bottle cap": "bottle_cap",
    "Metal bottle cap": "bottle_cap",
    
    # Plastic Bags & Film
    "Plastic film": "plastic_bag",
    "Plastic bag & wrapper": "plastic_bag",
    "Single-use carrier bag": "plastic_bag",
    "Polypropylene bag": "plastic_bag",
    "Crisp packet": "plastic_bag",
    "Garbage bag": "plastic_bag",
    "Other plastic wrapper": "plastic_bag",
    
    # Cans & Containers (Metal)
    "Food Can": "container",
    "Drink can": "container",
    "Aerosol": "container",
    
    # Cups
    "Paper cup": "cup",
    "Disposable plastic cup": "cup",
    "Foam cup": "cup",
    "Glass cup": "cup",
    "Other plastic cup": "cup",
    
    # Straws
    "Plastic straw": "straw",
    "Paper straw": "straw",
    
    # Plastic Containers
    "Disposable food container": "container",
    "Foam food container": "container",
    "Other plastic container": "container",
    "Spread tub": "container",
    "Tupperware": "container",
    
    # Cartons
    "Other carton": "container",
    "Egg carton": "container",
    "Drink carton": "container",
    "Corrugated carton": "container",
    "Meal carton": "container",
    "Pizza box": "container",
    
    # Plastic Items
    "Plastic lid": "plastic_bag",
    "Other plastic": "plastic_bag",
    "Plastic glooves": "plastic_bag",
    "Plastic utensils": "straw",
    "Six pack rings": "plastic_bag",
}

class WasteDetector:
    def __init__(self, model_path=None):
        self.model_path = model_path or Config.YOLO_MODEL_PATH
        self.model = None
        print(f"\n{'='*60}")
        print(f"[INIT] WasteDetector initializing...")
        print(f"[INIT] Model path: {self.model_path}")
        print(f"{'='*60}\n")
        self.load_model()
    
    def load_model(self):
        """Load YOLO model dari file .pt"""
        if not os.path.exists(self.model_path):
            print(f"[WARNING] ❌ Model tidak ditemukan di: {self.model_path}")
            print("[INFO] → Menggunakan demo mode (tanpa deteksi asli)\n")
            self.model = None
            return
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            
            print(f"[INFO] ✅ YOLO model loaded from: {self.model_path}")
            print(f"[INFO] Classes detected in model:")
            
            # Print hanya beberapa class untuk tidak spam console
            class_count = len(self.model.names)
            print(f"       Total classes: {class_count}")
            
            # Print beberapa contoh
            print("       Sample classes:")
            for i, (idx, name) in enumerate(list(self.model.names.items())[:5]):
                mapped = CLASS_MAPPING.get(name, name)
                print(f"         - {name} → {mapped}")
            print(f"         ... and {class_count - 5} more classes")
            print()

        except Exception as e:
            print(f"[ERROR] ❌ Gagal load YOLO model: {e}")
            print("[INFO] → Menggunakan demo mode (tanpa deteksi asli)\n")
            self.model = None
    
    def detect(self, image):
        """Deteksi sampah pada gambar"""
        if self.model is None:
            print("[DETECT] Using demo mode (no real model)")
            return self._demo_detection(image)

        try:
            # Convert PIL to numpy array
            img_array = np.array(image)
            
            # Run YOLO detection
            print(f"[DETECT] Running YOLO inference on image {image.size}...")
            results = self.model(img_array, verbose=False)

            detections = []
            raw_detections = []  # For logging

            for r in results:
                boxes = r.boxes
                
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    raw_label = self.model.names[cls]
                    
                    raw_detections.append({
                        'label': raw_label,
                        'conf': conf,
                        'accepted': conf >= Config.DETECTION_CONFIDENCE_THRESHOLD
                    })

                    if conf >= Config.DETECTION_CONFIDENCE_THRESHOLD:
                        # Mapping label ke versi yang disederhanakan
                        mapped_label = CLASS_MAPPING.get(raw_label, raw_label)

                        detections.append({
                            'class': mapped_label,
                            'confidence': conf,
                            'box': box.xyxy[0].tolist()
                        })

            # Logging
            print(f"[DETECT] Found {len(boxes)} objects")
            print(f"[DETECT] Accepted (conf >= {Config.DETECTION_CONFIDENCE_THRESHOLD}): {len(detections)}")
            
            # Print detail deteksi
            for det in raw_detections[:5]:  # Print max 5
                status = "✓" if det['accepted'] else "✗"
                print(f"[DETECT]   {status} {det['label']} ({det['conf']:.2f})")
            
            if len(raw_detections) > 5:
                print(f"[DETECT]   ... and {len(raw_detections) - 5} more")
            print()

            # Create annotated image
            annotated_array = results[0].plot()
            annotated_image = Image.fromarray(annotated_array)

            return detections, annotated_image

        except Exception as e:
            print(f"[ERROR] Detection error: {e}")
            import traceback
            traceback.print_exc()
            return self._demo_detection(image)
    
    def _demo_detection(self, image):
        """Fallback demo jika model gagal atau tidak ditemukan."""
        print("[DEMO] Running demo detection (fake results)")
        detections = [
            {'class': 'bottle', 'confidence': 0.75},
            {'class': 'plastic_bag', 'confidence': 0.65}
        ]
        return detections, image
    
    def calculate_points(self, waste_type):
        """Hitung poin berdasarkan jenis sampah"""
        points = Config.POINTS_MAP.get(
            waste_type.lower(),
            Config.POINTS_MAP['default']
        )
        return points