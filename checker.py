import time
import cv2
import numpy as np
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Constants
GIFT_FILE = "links.txt"  # File containing Discord gift links
VALID_GIFT_FILE = "valid_gifts.txt"  # File to store the first valid gift
ERROR_IMAGES_DIR = "error_images/"  # Folder with multiple "Invalid Gift Code" images
SCREENSHOT_PATH = "current_screenshot.png"  # Screenshot path
CROP_COORDS = (232, 255, 692, 602)  # (x1, y1, x2, y2) - Crop area
DELAY = 3  # ms delay per request

def load_gift_links():
    """Loads gift links from a text file."""
    with open(GIFT_FILE, "r") as file:
        return [line.strip() for line in file if line.strip()]

def save_valid_gift(link):
    """Saves the first valid gift link to a file."""
    with open(VALID_GIFT_FILE, "w") as file:
        file.write(link + "\n")

def take_screenshot(driver, link, save_path):
    """Takes a screenshot of the given link and saves it."""
    driver.get(link)
    time.sleep(0.5)  # Reduced wait time for page load
    driver.save_screenshot(save_path)

def crop_image(image_path, crop_coords):
    """Crops the screenshot to the specific area."""
    x1, y1, x2, y2 = crop_coords
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"❌ Failed to load image: {image_path}")

    cropped = image[y1:y2, x1:x2]  # Crop the region
    cv2.imwrite(image_path, cropped)  # Save the cropped image

def images_are_identical(img1_path, img2_path):
    """Compares two images and returns True if they are identical."""
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        raise ValueError("❌ One or both images could not be loaded!")

    # Resize images to the same shape (if needed)
    img1 = cv2.resize(img1, (img2.shape[1], img2.shape[0]))

    # Compute absolute difference
    diff = cv2.absdiff(img1, img2)

    # If the difference is completely zero, images are identical
    return np.count_nonzero(diff) == 0

def is_invalid_gift(screenshot_path):
    """Checks if the screenshot matches any known invalid gift screen."""
    for error_img in os.listdir(ERROR_IMAGES_DIR):
        error_img_path = os.path.join(ERROR_IMAGES_DIR, error_img)
        if images_are_identical(screenshot_path, error_img_path):
            return True  # Found a match, it's invalid
    return False  # No matches found, it's valid

def check_gift_link(driver, link):
    """Checks if a Discord gift link is valid by comparing screenshots."""
    take_screenshot(driver, link, SCREENSHOT_PATH)
    crop_image(SCREENSHOT_PATH, CROP_COORDS)  # Crop only the relevant area

    if is_invalid_gift(SCREENSHOT_PATH):
        print(f"❌ Invalid Gift: {link}")
        return False
    else:
        print(f"✅ Valid Gift Found: {link}")
        save_valid_gift(link)
        return True

def main():
    """Runs the gift code checker."""
    gift_links = load_gift_links()
    if not gift_links:
        print("⚠️ No gift links found in the file.")
        return

    # Setup Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        for link in gift_links:
            start_time = time.time()  # Track start time

            if check_gift_link(driver, link):  # If valid, save and stop
                print("🎉 Stopping... Valid link saved!")
                break

            # Ensure delay per request
            elapsed_time = time.time() - start_time
            if elapsed_time < DELAY:
                time.sleep(DELAY - elapsed_time)
                
        else:
            print("❌ No valid gift codes found.")
    finally:
        driver.quit()  # Close the browser

if __name__ == "__main__":
    main()
