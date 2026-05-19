"""
Setup script for prostate MRI segmentation tool
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prostate-segmentator",
    version="1.0.0",
    author="Prostate Segmentation Team",
    author_email="team@prostate-segmentation.org",
    description="A graphic segmentation tool for prostate MRI exams based on DICOM data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/prostate-segmentator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Medical Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "pydicom>=2.2.0",
        "pillow>=8.0.0",
        "opencv-python>=4.5.0",
        "scikit-image>=0.18.0",
        "scipy>=1.7.0",
        "PyQt5>=5.15.0",
        "flask>=2.0.0",
        "flask-socketio>=5.0.0",
        "flask-login>=0.5.0",
        "flask-sqlalchemy>=2.5.0",
        "torch>=1.9.0",
        "torchvision>=0.10.0",
        "segmentation-models-pytorch>=0.3.0",
        "h5py>=3.1.0",
        "nibabel>=3.2.0",
        "tqdm>=4.60.0",
        "pyyaml>=5.4.0",
    ],
    entry_points={
        "console_scripts": [
            "prostate-segmentator=src.main_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/*", "models/*", "templates/*"],
    },
    zip_safe=False,
)