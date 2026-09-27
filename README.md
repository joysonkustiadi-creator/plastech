# PlasTech

An AI-powered web application for detecting and managing plastic waste through a point-based gamification system. Built with Streamlit and YOLOv8 to encourage proper plastic waste disposal habits.

**Live demo:** [plastech.streamlit.app](https://plastech.streamlit.app/)

## Description

PlasTech is a smart waste management system that uses Computer Vision (YOLOv8) to detect plastic waste from photos, then rewards users with points as an incentive to dispose of that waste properly within a given time window. Inspired by gamification concepts to encourage environmentally friendly behavior.

## Key Features

- **Login & Register**: User authentication system with password hashing (SHA256)
- **Waste Detection**: Upload a photo or use the camera to detect plastic waste using a custom-trained YOLOv8 model (60 waste object classes)
- **Point System with Expiry**: Points are earned from detection, but expire if the waste isn't disposed of within 24 hours
- **Waste Disposal**: Verify disposal by scanning a QR code at the trash bin/collection point (detected directly from an uploaded photo using OpenCV) and uploading a proof-of-disposal photo
- **Leaderboard**: User ranking based on total points collected
- **Profile**: Personal statistics, activity history, and success rate

## Tech Stack

- **Frontend and Backend**: Streamlit
- **AI/Computer Vision**: YOLOv8 (Ultralytics), custom-trained on a plastic waste dataset
- **QR Code**: qrcode (generation), OpenCV QRCodeDetector (scanning/decoding)
- **Database**: SQLite
- **Image Processing**: Pillow, OpenCV (headless)
- **Others**: Pandas, NumPy

## Project Structure

```
PlasTech/
├── app.py                  # Application entry point
├── config.py                # Configuration (points, threshold, model path, etc.)
├── database_manager.py       # Database CRUD operations (SQLite)
├── yolo_detector.py         # YOLO detection wrapper
├── qr_scanner.py             # QR code scanning/decoding from images (OpenCV)
├── auth.py                  # Password hashing and verification utilities
├── qr_generator.py          # QR code generation for disposal
├── image_processor.py       # Image conversion and resizing utilities
├── sidebar.py                # Sidebar navigation component
├── stats_card.py             # Statistics card component
├── page_login.py             # Login/register page
├── page_home.py              # Main dashboard page
├── page_detect.py            # Waste detection page
├── page_dispose.py           # Waste disposal page
├── page_leaderboard.py       # Leaderboard page
├── page_profile.py           # User profile page
├── waste_detection.pt        # Trained YOLOv8 model weights
├── requirements.txt          # Python dependencies
├── packages.txt              # System-level dependencies (for Streamlit Cloud)
└── runtime.txt               # Python version pin
```

## Installation and Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/joysonkustiadi-creator/plastech.git
cd plastech
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## How to Use

1. Register a new account or log in if you already have one
2. On the Home page, click "Start Detection"
3. Upload a photo or take a picture of plastic waste using the camera
4. The system will detect the waste type and calculate the points you can earn
5. Click "Save Detection". The points remain active for 24 hours
6. Dispose of the waste at a trash bin/collection point that provides a QR code within 24 hours
7. On the "Dispose Waste" page, upload a photo containing the QR code (scanned automatically) or enter the code manually, then upload a proof-of-disposal photo
8. Points are automatically credited to your account after confirmation
9. Check the Leaderboard to see the rankings, or Profile to view your personal history and stats

## AI Model

The detection model uses YOLOv8n, trained on a custom dataset based on TACO-style waste categories, covering 60 object classes such as plastic bottles, bottle caps, plastic bags, cups, food packaging, and more. These classes are then mapped to simplified PlasTech point categories (bottle, bottle_cap, plastic_bag, cup, container, straw, etc.) via CLASS_MAPPING in yolo_detector.py.

The dataset and model training pipeline are kept separate from this repository to keep the repo size lightweight. Only the final weight file (waste_detection.pt) is used by the application.

## Deployment

This application is deployed on Streamlit Community Cloud. A few points worth noting for anyone redeploying or forking this project:

- **Python version**: pinned via `runtime.txt` and the app's Python version setting in the Streamlit Cloud dashboard, to ensure prebuilt wheels are available for all dependencies (avoids build failures on newer Python versions)
- **System libraries**: `packages.txt` installs `libgl1` and `libglib2.0-0`, required by OpenCV when running in a headless server environment
- **OpenCV**: uses `opencv-python-headless` instead of the regular `opencv-python` package, since the server has no display
- **QR scanning**: implemented with OpenCV's built-in `QRCodeDetector` rather than `pyzbar`, to avoid an additional native system dependency (`libzbar`) that proved unreliable on Streamlit Cloud

## Notes

- The application uses a local SQLite database (`plastech.db`) that is automatically created the first time the app runs
- Storage on Streamlit Community Cloud is ephemeral: the database resets whenever the app is redeployed, rebooted, or wakes up from being idle. This is a known limitation of the free hosting tier and is acceptable for demo/coursework purposes. For persistent data, the database would need to be migrated to an externally hosted database
- The detection confidence threshold can be adjusted in `config.py` via `DETECTION_CONFIDENCE_THRESHOLD`

## Author

Joshua Joyson Kustiadi
Computer Science Student, Bina Nusantara University (BINUS)

## License

This project was built for an Artificial Intelligence coursework assignment.