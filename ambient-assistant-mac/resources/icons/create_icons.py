#!/usr/bin/env python3
"""
Script to create icon files for Ambient Assistant.
This creates placeholder icons that can be replaced with better designs later.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_app_icon():
    """Create the main application icon."""
    img = Image.new('RGBA', (512, 512), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circular background
    draw.ellipse((50, 50, 462, 462), fill=(40, 120, 200, 255))
    
    # Draw a stylized "A" in the center
    try:
        # Try to use a system font
        font = ImageFont.truetype("Arial", 300)
    except IOError:
        # Fall back to default
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((160, 60), "A", fill=(255, 255, 255, 255), font=font)
    
    # Save image
    img.save('app_icon.png')
    print("Created app_icon.png")

def create_status_icons():
    """Create status icons for the application tray."""
    # Active icon (green)
    img = Image.new('RGBA', (128, 128), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((20, 20, 108, 108), fill=(40, 180, 100, 255))
    draw.ellipse((48, 48, 80, 80), fill=(255, 255, 255, 255))
    img.save('active.png')
    print("Created active.png")
    
    # Inactive icon (gray)
    img = Image.new('RGBA', (128, 128), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((20, 20, 108, 108), fill=(150, 150, 150, 255))
    draw.ellipse((48, 48, 80, 80), fill=(255, 255, 255, 255))
    img.save('inactive.png')
    print("Created inactive.png")
    
    # Processing icon (blue with animation hint)
    img = Image.new('RGBA', (128, 128), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((20, 20, 108, 108), fill=(40, 120, 200, 255))
    draw.arc((48, 48, 80, 80), start=0, end=270, fill=(255, 255, 255, 255), width=4)
    img.save('processing.png')
    print("Created processing.png")

if __name__ == "__main__":
    # Change to the icons directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    create_app_icon()
    create_status_icons()
    print("All icons created successfully.") 