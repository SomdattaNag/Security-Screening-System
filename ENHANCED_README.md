# Enhanced Security Screening System

This is an enhanced version of the Security Screening System with advanced features including face recognition, real-time alerts, and improved logging.

## Features

### Face Recognition
- Uses MTCNN for accurate face detection
- Recognizes known faces from the `known_faces` directory
- Highlights unknown faces in red
- Tracks and logs all detections

### Real-time Alerts
- Email notifications for security events
- Sound alerts for immediate feedback
- Configurable alert cooldown period

### Enhanced Logging
- CSV-based logging with timestamps
- Stores confidence scores for detections
- Saves images of detected events
- Logs all system activities

### Security Features
- Motion detection
- Night vision mode (coming soon)
- Secure configuration via .env file

## Requirements
- Python 3.7+
- Webcam
- Internet connection (for email alerts)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Security-Screening-System.git
   cd Security-Screening-System
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements-enhanced.txt
   ```

4. Set up your `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your email credentials and settings.

## Usage

1. Add known faces to the `known_faces` directory:
   - Place one image per person
   - Name the file with the person's name (e.g., `john_doe.jpg`)

2. Run the security system:
   ```bash
   python enhanced_security_system.py
   ```

3. The system will start and begin monitoring your webcam feed
   - Known faces will be highlighted in green with their names
   - Unknown faces will be highlighted in red
   - Events will be logged to `logs/security_log.csv`
   - Images will be saved to the `image_logs` directory

4. Press 'q' to quit the application

## Configuration

Edit the `.env` file to configure:
- Email alerts
- Alert thresholds
- Logging options

## Logs

All security events are logged to `logs/security_log.csv` with the following columns:
- `timestamp`: When the event occurred
- `event_type`: Type of event (e.g., "UnknownPerson", "MotionDetected")
- `confidence`: Detection confidence (0-1)
- `location`: Location in the frame (x1,y1-x2,y2)
- `image_path`: Path to the saved image (if any)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
