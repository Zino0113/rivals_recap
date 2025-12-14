import cv2
import numpy as np
from PIL import Image

# Load the image
image_path = "icons.png"
image = cv2.imread(image_path)
original_image = Image.open(image_path)

# Convert to RGB for PIL saving later
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Get dimensions
height, width, _ = image.shape

# The image is a 2x4 grid. We will slice it dynamically.
# Defining the grid structure
rows = 2
cols = 4

# Calculate rough cell dimensions
cell_h = height // rows
cell_w = width // cols

# Icon names based on the image text
icon_names = [
    ["신화_파괴자", "거인_학살자", "셧다운", "여기까지입니다"],
    ["돌격", "손이_시려워_꽁", "웨폰_마스터", "넌_못_지나간다"]
]

cropped_files = []

# Padding to avoid the very edges/lines between buttons (optional, but makes it cleaner)
# Looking at the image, there are gaps. Let's try to center-crop or just crop the grid cell.
# We will do a simple grid crop first to ensure we get everything.
padding_x = int(cell_w * 0.02) # 2% padding
padding_y = int(cell_h * 0.02)

for r in range(rows):
    for c in range(cols):
        # Calculate coordinates
        x1 = c * cell_w + padding_x
        y1 = r * cell_h + padding_y
        x2 = (c + 1) * cell_w - padding_x
        y2 = (r + 1) * cell_h - padding_y
        
        # Crop
        cropped_img = original_image.crop((x1, y1, x2, y2))
        
        # Save file
        file_name = f"{icon_names[r][c]}.png"
        cropped_img.save(file_name)
        cropped_files.append(file_name)

cropped_files