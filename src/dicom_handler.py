"""
DICOM Handler for Prostate MRI exams
Handles reading, parsing, and managing DICOM data for segmentation
"""

import pydicom
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np


class DICOMHandler:
    """Handles DICOM data operations for prostate MRI exams"""

    def __init__(self):
        self.series_data = {}
        self.patient_data = {}

    def load_series_from_directory(self, directory: str) -> Dict:
        """
        Load all DICOM series from a directory

        Args:
            directory: Path to directory containing DICOM files

        Returns:
            Dictionary with series information
        """
        series_dict = {}
        files = []

        # Get all DICOM files in directory
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(('.dcm', '.DCM')):
                    files.append(os.path.join(root, filename))

        # Group files by SeriesInstanceUID
        series_groups = {}
        for file_path in files:
            try:
                ds = pydicom.dcmread(file_path)
                series_uid = ds.SeriesInstanceUID
                if series_uid not in series_groups:
                    series_groups[series_uid] = []
                series_groups[series_uid].append(file_path)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

        # Process each series
        for series_uid, file_list in series_groups.items():
            try:
                # Load first file to get series info
                ds = pydicom.dcmread(file_list[0])
                series_info = {
                    'series_uid': series_uid,
                    'series_name': getattr(ds, 'SeriesDescription', 'Unknown Series'),
                    'modality': getattr(ds, 'Modality', 'Unknown'),
                    'patient_id': getattr(ds, 'PatientID', 'Unknown'),
                    'study_uid': getattr(ds, 'StudyInstanceUID', 'Unknown'),
                    'files': file_list,
                    'num_files': len(file_list),
                    'data': self._load_series_data(file_list)
                }
                series_dict[series_uid] = series_info
            except Exception as e:
                print(f"Error processing series {series_uid}: {e}")
                continue

        return series_dict

    def _load_series_data(self, file_list: List[str]) -> np.ndarray:
        """
        Load 3D data from a series of DICOM files

        Args:
            file_list: List of DICOM file paths

        Returns:
            3D numpy array with the image data
        """
        try:
            # Read first file to get dimensions
            ds = pydicom.dcmread(file_list[0])
            rows = ds.Rows
            cols = ds.Columns
            num_slices = len(file_list)

            # Create 3D array
            volume = np.zeros((num_slices, rows, cols), dtype=np.float32)

            # Load each slice
            for i, file_path in enumerate(file_list):
                ds = pydicom.dcmread(file_path)
                volume[i] = ds.pixel_array.astype(np.float32)

            return volume
        except Exception as e:
            print(f"Error loading series data: {e}")
            return None

    def get_patient_info(self, series_info: Dict) -> Dict:
        """
        Extract patient information from series

        Args:
            series_info: Dictionary with series information

        Returns:
            Patient information dictionary
        """
        patient_info = {
            'patient_id': series_info.get('patient_id', 'Unknown'),
            'patient_name': series_info.get('patient_name', 'Unknown'),
            'patient_birth_date': series_info.get('PatientBirthDate', 'Unknown'),
            'study_date': series_info.get('StudyDate', 'Unknown'),
            'study_description': series_info.get('StudyDescription', 'Unknown'),
            'modality': series_info.get('modality', 'Unknown')
        }
        return patient_info

    def get_series_info(self, series_dict: Dict) -> List[Dict]:
        """
        Get list of series information

        Args:
            series_dict: Dictionary with series information

        Returns:
            List of series information
        """
        series_list = []
        for series_uid, series_info in series_dict.items():
            info = {
                'series_uid': series_uid,
                'series_name': series_info['series_name'],
                'modality': series_info['modality'],
                'num_files': series_info['num_files'],
                'patient_id': series_info['patient_id']
            }
            series_list.append(info)
        return series_list