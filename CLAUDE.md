# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a prostate MRI segmentation tool that provides both a desktop GUI application and a web-based interface for medical professionals to annotate and segment prostate MRI exams. The tool supports multi-series DICOM handling, various annotation tools, status tracking, and multi-user collaboration features.

## Architecture

The application is organized into several key components:

1. **GUI Application** (`src/main_app.py`): PyQt5-based desktop application with main UI
2. **DICOM Handling** (`src/dicom_handler.py`): Reads and processes DICOM files for MRI data
3. **Segmentation Tools** (`src/segmentation_tools.py`): Core segmentation algorithms including brush, rectangle, circle, flood fill, threshold, watershed, and active contour tools
4. **Status Tracking** (`src/status_tracker.py`): Tracks segmentation progress and user activities
5. **User Management** (`src/user_manager.py`): Handles multi-user authentication and session management
6. **Web Interface** (`src/web_interface.py`): Flask-based web API with SocketIO for real-time collaboration
7. **Configuration** (`src/config.py`): Centralized configuration management

## Key Features

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

## Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### GUI Application
```bash
python src/main_app.py
```

### Web Interface
```bash
python src/web_interface.py
```

The web interface will be available at `http://localhost:5000`

## Testing

Tests are located in the `tests/` directory and can be run with:
```bash
python -m pytest tests/
```

## Configuration

Configuration is handled through `src/config.py` and environment variables:
- `MULTI_USER_ENABLED`: Enable/disable multi-user support
- `DATABASE_URL`: Database connection string
- `AI_MODEL_PATH`: Path to AI models
- `WEB_HOST`/`WEB_PORT`: Web interface settings