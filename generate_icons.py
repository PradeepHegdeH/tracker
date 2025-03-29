from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    # Create a new image with a white background
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a green circle
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill='#4CAF50')
    
    # Add text
    try:
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "N"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    return image

# Generate icons of different sizes
sizes = [48, 128]
for size in sizes:
    icon = create_icon(size)
    icon.save(f'icon{size}.png')

print("Icons generated successfully!") 