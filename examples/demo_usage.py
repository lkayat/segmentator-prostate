"""
Demonstration of prostate MRI segmentation tool usage
"""

import numpy as np
from src.dicom_handler import DICOMHandler
from src.segmentation_tools import SegmentationTools
from src.status_tracker import StatusTracker
from src.user_manager import UserManager


def demo_dicom_handling():
    """Demonstrate DICOM handling functionality"""
    print("=== DICOM Handling Demo ===")

    # Initialize DICOM handler
    dicom_handler = DICOMHandler()

    print("DICOM handler initialized")
    print(f"Available methods: {dir(dicom_handler)}")

    # Note: Actual DICOM loading would require a DICOM directory
    print("Note: Actual DICOM loading requires a valid DICOM directory structure")


def demo_segmentation_tools():
    """Demonstrate segmentation tools functionality"""
    print("\n=== Segmentation Tools Demo ===")

    # Initialize segmentation tools
    seg_tools = SegmentationTools()

    print("Segmentation tools initialized")
    print(f"Available tools: {list(seg_tools.tools.keys())}")

    # Create a simple test image
    test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    print(f"Test image shape: {test_image.shape}")

    # Test threshold tool
    try:
        threshold_result = seg_tools.apply_tool('threshold', test_image, threshold_value=128)
        print(f"Threshold tool result shape: {threshold_result.shape}")
        print("Threshold tool executed successfully")
    except Exception as e:
        print(f"Error with threshold tool: {e}")

    # Test rectangle tool
    try:
        rectangle_result = seg_tools.apply_tool('rectangle', test_image, x1=10, y1=10, x2=50, y2=50, value=255)
        print(f"Rectangle tool result shape: {rectangle_result.shape}")
        print("Rectangle tool executed successfully")
    except Exception as e:
        print(f"Error with rectangle tool: {e}")


def demo_status_tracking():
    """Demonstrate status tracking functionality"""
    print("\n=== Status Tracking Demo ===")

    # Initialize status tracker
    status_tracker = StatusTracker()

    print("Status tracker initialized")
    print(f"Status data: {status_tracker.status_data}")
    print(f"User activities: {status_tracker.user_activities}")


def demo_user_management():
    """Demonstrate user management functionality"""
    print("\n=== User Management Demo ===")

    # Initialize user manager
    user_manager = UserManager()

    print("User manager initialized")
    print(f"Users: {user_manager.users}")
    print(f"Sessions: {user_manager.sessions}")


def demo_ai_integration():
    """Demonstrate AI pre-segmentation integration"""
    print("\n=== AI Integration Demo ===")

    seg_tools = SegmentationTools()

    # Create a simple test image
    test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)

    try:
        # Test AI pre-segmentation
        ai_result = seg_tools.pre_segmentation_ai(test_image, model_type="unet")
        print(f"AI pre-segmentation result shape: {ai_result.shape}")
        print("AI pre-segmentation executed successfully")
    except Exception as e:
        print(f"Error with AI pre-segmentation: {e}")


def main():
    """Main demo function"""
    print("Prostate MRI Segmentation Tool - Demo")
    print("=" * 50)

    demo_dicom_handling()
    demo_segmentation_tools()
    demo_status_tracking()
    demo_user_management()
    demo_ai_integration()

    print("\n" + "=" * 50)
    print("Demo completed successfully!")


if __name__ == "__main__":
    main()