#!/usr/bin/env python3
"""
Ambient Assistant setup script.

This script handles the installation of the Ambient Assistant application
and its dependencies.
"""

import os
import sys
from setuptools import setup, find_packages

# Check Python version
if sys.version_info < (3, 9):
    sys.exit("Error: Ambient Assistant requires Python 3.9 or later")

# Read the README for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define dependencies
INSTALL_REQUIRES = [
    # Core dependencies
    "PyQt6>=6.4.0",
    "Django>=4.2.0",
    "pillow>=9.4.0",
    "opencv-python>=4.7.0.72",
    "numpy>=1.23.0",
    "pynput>=1.7.6",
    "pyobjc>=9.0.1",  # For macOS integration
    "darkdetect>=0.8.0",  # For detecting system theme
    "python-dotenv>=1.0.0",
    "requests>=2.28.0",
    
    # OCR dependencies
    "pytesseract>=0.3.10",
    
    # LLM dependencies
    "openai>=1.1.0",
    "anthropic>=0.5.0",
    "langchain>=0.0.267",
    "langchain-openai>=0.0.2",
    "langchain-anthropic>=0.1.1",
    "langchainhub>=0.1.13",
    "langgraph>=0.0.15",
    "sentence-transformers>=2.2.2",  # For semantic searching
    
    # NLP dependencies
    "spacy>=3.6.0",
    
    # Packaging and distribution
    "pyinstaller>=5.9.0",
    'sounddevice',
    'soundfile',
    'pygame',
    'openai>=1.0.0',
    "pyautogui>=0.9.53",
    "langchain-community>=0.0.10",
    "sounddevice>=0.4.6",
    "soundfile>=0.12.1",
    "numpy>=1.20.0"
]

# Define optional dependencies
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
    ],
    "spacy": [
        "spacy-transformers>=1.2.5",
    ],
}

# Entry points
ENTRY_POINTS = {
    "console_scripts": [
        "ambient-assistant=ambient.app:main",
    ],
}

# Define package data
PACKAGE_DATA = {
    "ambient": [
        "resources/icons/*.png",
        "resources/icons/*.icns",
        "resources/styles/*.css",
        "resources/sounds/*.wav",
    ],
}

# Main setup configuration
setup(
    name="ambient-assistant",
    version="0.1.0",
    author="Ambient Team",
    author_email="info@ambient-assistant.com",
    description="An AI-powered ambient coding assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ambient-team/ambient-assistant",
    packages=find_packages(),
    package_data=PACKAGE_DATA,
    include_package_data=True,
    entry_points=ENTRY_POINTS,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: MacOS X",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment :: Assistants",
    ],
)


def post_install():
    """Run post-installation steps."""
    # Download spaCy models
    try:
        import spacy
        spacy.cli.download("en_core_web_sm")
        print("Downloaded spaCy language model: en_core_web_sm")
    except Exception as e:
        print(f"Error downloading spaCy model: {e}")
        print("You can manually download it with: python -m spacy download en_core_web_sm")


if __name__ == "__main__" and "install" in sys.argv:
    # Run post-install steps after setup
    setup_args = sys.argv.copy()
    sys.argv = [sys.argv[0]] + [arg for arg in sys.argv[1:] if arg != "--run-post-install"]
    
    if "--run-post-install" in setup_args:
        post_install()
