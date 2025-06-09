"""
Setup script for Earth Image Downloader (eimg)
Copyright (c) 2025 Kozosvyst Stas (STASX)
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="eimg",
    version="0.0.2",
    author="Kozosvyst Stas (STASX)",
    author_email="dev@sxservisecli.tech",
    description="A secure command-line tool to download Earth images from NASA's EPIC API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StasX-Official/Photo-of-the-earth",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.28.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "eimg=main:main",
        ],
    },
    keywords="nasa epic earth satellite space astronomy photography",
    project_urls={
        "Bug Reports": "https://github.com/StasX-Official/Photo-of-the-earth/issues",
        "Source": "https://github.com/StasX-Official/Photo-of-the-earth",
        "Documentation": "https://github.com/StasX-Official/Photo-of-the-earth/blob/main/LEARN.md",
    },
)
