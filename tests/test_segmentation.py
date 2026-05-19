"""
Test suite for prostate MRI segmentation tool
"""

import unittest
import numpy as np
from src.dicom_handler import DICOMHandler
from src.segmentation_tools import SegmentationTools
from src.status_tracker import StatusTracker
from src.user_manager import UserManager


class TestDICOMHandler(unittest.TestCase):
    """Test DICOM handler functionality"""

    def setUp(self):
        self.handler = DICOMHandler()

    def test_initialization(self):
        """Test DICOM handler initialization"""
        self.assertIsNotNone(self.handler)
        self.assertEqual(self.handler.series_data, {})
        self.assertEqual(self.handler.patient_data, {})


class TestSegmentationTools(unittest.TestCase):
    """Test segmentation tools functionality"""

    def setUp(self):
        self.tools = SegmentationTools()

    def test_tool_initialization(self):
        """Test segmentation tools initialization"""
        self.assertIsNotNone(self.tools)
        self.assertIn('brush', self.tools.tools)
        self.assertIn('rectangle', self.tools.tools)
        self.assertIn('circle', self.tools.tools)
        self.assertIn('flood_fill', self.tools.tools)
        self.assertIn('threshold', self.tools.tools)
        self.assertIn('watershed', self.tools.tools)
        self.assertIn('active_contour', self.tools.tools)

    def test_threshold_tool(self):
        """Test threshold tool functionality"""
        # Create a simple test image
        test_image = np.array([[100, 200, 150], [50, 255, 75]], dtype=np.uint8)

        # Apply threshold tool
        result = self.tools.apply_tool('threshold', test_image, threshold_value=128)

        # Check that result is a binary array
        self.assertEqual(result.shape, test_image.shape)
        self.assertTrue(np.all((result == 0) | (result == 255)))


class TestStatusTracker(unittest.TestCase):
    """Test status tracker functionality"""

    def setUp(self):
        self.tracker = StatusTracker()

    def test_status_tracker_initialization(self):
        """Test status tracker initialization"""
        self.assertIsNotNone(self.tracker)
        self.assertEqual(self.tracker.status_data, {})
        self.assertEqual(self.tracker.user_activities, [])


class TestUserManager(unittest.TestCase):
    """Test user manager functionality"""

    def setUp(self):
        self.user_manager = UserManager()

    def test_user_manager_initialization(self):
        """Test user manager initialization"""
        self.assertIsNotNone(self.user_manager)
        self.assertEqual(self.user_manager.users, {})
        self.assertEqual(self.user_manager.sessions, {})


if __name__ == '__main__':
    unittest.main()