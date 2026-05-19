# Prostate MRI Segmentation Tool

A graphic segmentation tool for prostate MRI exams based on DICOM data with multi-series handling, annotation tools, status tracking, and multi-user support.

## Features

- **DICOM Multi-series Handling**: Support for loading and managing multiple DICOM series and sequences
- **Annotation and Segmentation Tools**: 
  - Brush tool
  - Rectangle tool
  - Circle tool
  - Flood fill tool
  - Threshold tool
  - Watershed tool
  - Active contour tool
- **Status Tracking**: Comprehensive tracking of segmentation progress and user activities
- **Multi-user Support**: Web-based interface with user authentication and session management
- **AI Integration**: Pre-segmentation capabilities using AI models
- **Real-time Collaboration**: Support for multiple users working on the same task

## Architecture

```
prostate_segmentation/
├── src/
│   ├── __init__.py
│   ├── main_app.py              # Main GUI application
│   ├── dicom_handler.py         # DICOM data handling
│   ├── segmentation_tools.py    # Core segmentation tools
│   ├── status_tracker.py        # Status tracking system
│   ├── user_manager.py          # Multi-user support
│   ├── web_interface.py         # Web API and real-time features
│   ├── config.py                # Configuration settings
│   └── models/                  # AI models directory
├── data/                        # Data storage
│   ├── user_data/               # User information
│   ├── segmentations/           # Segmentation results
│   └── dicom/                   # DICOM data
├── notebooks/                   # Jupyter notebooks for research
├── tests/                       # Test files
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd prostate_segmentation
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the GUI Application

```bash
python src/main_app.py
```

### Running the Web Interface

```bash
python src/web_interface.py
```

The web interface will be available at `http://localhost:5000`

### Loading DICOM Data

1. Open the application
2. Go to File → Open DICOM Series
3. Select the folder containing your DICOM files
4. The application will load all series in the folder

### Segmentation Workflow

1. Load DICOM series
2. Select segmentation tool from the Tools tab
3. Apply tools to annotate regions of interest
4. Use AI pre-segmentation for initial segmentation
5. Refine manual annotations
6. Save the final segmentation

## Multi-user Support

The tool supports multi-user environments with:

- User authentication and session management
- Role-based access control
- Real-time collaboration features
- Activity tracking and audit logs

## AI Pre-segmentation

The tool includes integration with AI models for:

- Automated pre-segmentation
- Initial region detection
- Speeding up manual annotation
- Quality improvement

## Configuration

The application can be configured through environment variables or the `config.py` file:

- `MULTI_USER_ENABLED`: Enable/disable multi-user support
- `DATABASE_URL`: Database connection string
- `AI_MODEL_PATH`: Path to AI models
- `WEB_HOST`/`WEB_PORT`: Web interface settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Acknowledgments

- DICOM handling powered by pydicom
- GUI framework using PyQt5
- AI models from segmentation-models-pytorch
- Web framework using Flask and SocketIO