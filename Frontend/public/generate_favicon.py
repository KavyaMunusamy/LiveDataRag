from PIL import Image, ImageDraw
import base64
import os

# Create main icon (32x32)
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)]

for size in icon_sizes:
    img = Image.new('RGBA', size, (25, 118, 210, 255))  # #1976d2
    draw = ImageDraw.Draw(img)
    
    # Draw AI/RAG symbol
    width, height = size
    padding = width // 5
    
    # Draw brain/network symbol
    center_x, center_y = width // 2, height // 2
    radius = min(center_x, center_y) - padding
    
    # Outer circle
    draw.ellipse(
        [center_x - radius, center_y - radius, 
         center_x + radius, center_y + radius],
        outline='white', width=2
    )
    
    # Inner connections
    if size[0] >= 32:
        # Draw connecting lines
        for angle in range(0, 360, 45):
            rad = angle * 3.14159 / 180
            x1 = center_x + (radius * 0.7) * math.cos(rad)
            y1 = center_y + (radius * 0.7) * math.sin(rad)
            x2 = center_x + (radius * 0.3) * math.cos(rad)
            y2 = center_y + (radius * 0.3) * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill='white', width=1)
    
    # Save individual icons
    img.save(f'favicon_{size[0]}x{size[1]}.png')

print("Icons generated! Use favicon.io to convert to .ico format")