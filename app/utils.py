# utils.py (new file)
import os
import secrets
from PIL import Image
from flask import current_app

def save_profile_picture(form_picture):
    """
    Save profile picture and return the filename
    """
    # Generate random filename to prevent duplicates
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # Create path for saving
    pictures_dir = os.path.join(current_app.root_path, 'static/profile_pics')
    
    # Create directory if it doesn't exist
    if not os.path.exists(pictures_dir):
        os.makedirs(pictures_dir)
        
    picture_path = os.path.join(pictures_dir, picture_fn)
    
    # Resize image (crop to square)
    output_size = (200, 200)
    i = Image.open(form_picture)
    
    # Crop to square
    width, height = i.size
    if width > height:
        left = (width - height) / 2
        top = 0
        right = width - (width - height) / 2
        bottom = height
    else:
        left = 0
        top = (height - width) / 2
        right = width
        bottom = height - (height - width) / 2
    
    i = i.crop((left, top, right, bottom))
    i = i.resize(output_size)
    i.save(picture_path)
    
    return os.path.join('profile_pics', picture_fn)