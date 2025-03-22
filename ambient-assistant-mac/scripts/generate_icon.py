#!/usr/bin/env python
"""
Generate a simple app icon for the Ambient Assistant.
This requires the Pillow library.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def generate_icon():
    """Generate a simple gradient app icon with text."""
    # Create a new image with transparent background
    size = (512, 512)
    img = Image.new('RGBA', size, color=(0, 0, 0, 0))
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Create a gradient background (dark gray)
    for y in range(size[1]):
        for x in range(size[0]):
            # Calculate distance from center
            distance = ((x - size[0] / 2) ** 2 + (y - size[1] / 2) ** 2) ** 0.5
            max_distance = ((size[0] / 2) ** 2 + (size[1] / 2) ** 2) ** 0.5
            
            # Calculate gradient factor
            factor = distance / max_distance
            
            # Set dark gray gradient
            r = int(60 - 30 * factor)
            g = int(60 - 30 * factor)
            b = int(65 - 30 * factor)
            
            draw.point((x, y), fill=(r, g, b, 255))
    
    # Draw a circle
    circle_size = int(size[0] * 0.8)
    circle_pos = ((size[0] - circle_size) // 2, (size[1] - circle_size) // 2)
    draw.ellipse(
        (circle_pos[0], circle_pos[1], circle_pos[0] + circle_size, circle_pos[1] + circle_size),
        outline=(200, 200, 200, 150),
        width=3
    )
    
    # Draw "AI" text - using default font to avoid issues
    # Pillow's font handling has changed between versions
    font = ImageFont.load_default()
    
    # Draw with a simple method that works across all Pillow versions
    text = "AI"
    # Place text in the center approximately
    text_position = (size[0] // 2 - 50, size[1] // 2 - 50)
    
    # Add text with shadow
    shadow_offset = 5
    draw.text((text_position[0] + shadow_offset, text_position[1] + shadow_offset), text, fill=(30, 30, 35, 180))
    draw.text(text_position, text, fill=(220, 220, 230, 255))
    
    # Save the image
    icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ambient", "resources", "icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    icon_path = os.path.join(icon_dir, "app_icon.png")
    img.save(icon_path)
    print(f"Generated icon at: {icon_path}")
    
    # Create a simpler icon for ICO format
    # ICO format requires specific sizes, so we'll create a scaled version
    # without the heavy gradient computation
    ico_img = Image.new('RGBA', (256, 256), color=(40, 40, 45, 255))
    ico_draw = ImageDraw.Draw(ico_img)
    
    # Draw a circle
    ico_circle_size = 200
    ico_circle_pos = (28, 28)  # (256-200)/2 = 28
    ico_draw.ellipse(
        (ico_circle_pos[0], ico_circle_pos[1], ico_circle_pos[0] + ico_circle_size, ico_circle_pos[1] + ico_circle_size),
        outline=(200, 200, 200, 150),
        width=2
    )
    
    # Draw text
    ico_draw.text((110, 110), "AI", fill=(220, 220, 230, 255))
    
    # Save ICO
    ico_path = os.path.join(icon_dir, "app_icon.ico")
    ico_img.save(ico_path)
    print(f"Generated ICO icon at: {ico_path}")

if __name__ == "__main__":
    generate_icon() 