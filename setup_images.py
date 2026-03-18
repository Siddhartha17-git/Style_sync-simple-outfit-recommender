import os
import shutil

def setup_images():
    # Create outfit_images directory if it doesn't exist
    if not os.path.exists('outfit_images'):
        os.makedirs('outfit_images')
    
    # Copy existing images to outfit_images directory
    images_to_copy = [
        'lastbg.jpeg',
        'edit.jpeg',
        'IMG_8746.JPEG.jpg',
        'IMG_20250329_020608_upscaled (1).jpg'
    ]
    
    for i, img in enumerate(images_to_copy, 1):
        if os.path.exists(img):
            shutil.copy(img, f'outfit_images/outfit_{i}.jpg')
            print(f"Copied {img} to outfit_images/outfit_{i}.jpg")

if __name__ == "__main__":
    setup_images() 