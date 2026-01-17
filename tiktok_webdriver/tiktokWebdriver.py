from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# Housekeeping
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

# More housekeeping
tiktok_link = 'https://www.tiktok.com/en/'
driver.get(tiktok_link)
print(f"Opened: {tiktok_link}")

def promptLogin():
    # Prompt user to log in
    continue_prompt = ''
    while continue_prompt.lower() != 'y':
        continue_prompt = input("Enter Y after logging in to TikTok to continue: ")

    # Give time to switch windows
    wait_time = 5
    for i in range(wait_time, 0, -1):
        print(f"Scrolling in: {i}s...")
        time.sleep(1)
    print(f"Beginning interaction...")

def pressLikeButton():
    try:
        # Find the HTML element with the aria-label starting with "Like video" (like button). Wait for refresh if necessary.
        like_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label^='Like video']"))
        )

        # Click the button
        like_button.click()
        print("SUCCESS: Liked the video!")
        
    except Exception as e:
        print(f"FAILED: Could not find or click the button. Error: {e}")
        
def pressSaveButton():
    try:
        # Find the HTML element with the aria-label starting with "Add to Favorites." (save button). Wait for refresh if necessary.
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label^='Add to Favorites.']"))
        )

        # Click the button
        save_button.click()
        print("SUCCESS: Saved the video!")
        
    except Exception as e:
        print(f"FAILED: Could not find or click the button. Error: {e}")
        
def scroll():
    # Simulate down arrow keypress
    driver.find_element(By.TAG_NAME, "html").send_keys(Keys.ARROW_DOWN)

def quit():
    # Close the browser window
    print("Closing window.")
    driver.quit()
