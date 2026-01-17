from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
class TikTokWebdriverInstance: # _ indicates internal use
    def __init__(self):
        # Prepare driver options
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)

        # Initialize the driver
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def openTiktok(self):
        tiktok_link = 'https://www.tiktok.com/en/'
        self.driver.get(tiktok_link)
        print(f"Opened: {tiktok_link}")
        
    def promptLogin(self):
        print("(Remember to right press & click 'view video details' after logging in).")
        self._promptAction("logging in to tiktok")
        
    def _get_visible_element(self, css_selector):
        """
        Helper: returns the selector element that's onscreen (in viewport).
        AKA Tiktok keeps the HTML from previous videos LOADED but OFSCREEN >:( so we
        need to filter by the stuff thats onscreen.
        """
        # Get the height of the browser window
        viewport_height = self.driver.execute_script("return window.innerHeight")
        
        # Find ALL buttons that match the css selector
        elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
        
        for element in elements:
            try:
                # Get the element's Y position
                y_position = element.location['y']
                
                # Check if the element is onscreen (0 to viewport_height)
                if 0 < y_position < viewport_height:
                    return element
            except:
                continue
                
        raise Exception("No visible element found in viewport")
    
    def _rightClickActiveVideo(self):
        try:
            # get the media card
            active_video_card = self._get_visible_element("[id^='media-card']")
            
            # right click it
            action = ActionChains(self.driver)
            action.context_click(active_video_card).perform()
            
            print(f"Right-clicked video ID: {active_video_card.get_attribute('id')}")
            
        except Exception as e:
            print(f"FAILED: Could not right-click active video.\nError: {e}")
            
    def _pressEsc(self):
        try:
            # Send ESCAPE to the main body of the page
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            print("Sent ESCAPE key to dismiss menu.")
        except Exception as e:
            print(f"Could not dismiss menu: {e}")

    def _promptAction(self, action_description):
        # Prompt user to log in
        continue_prompt = ''
        while continue_prompt.lower() != 'y':
            continue_prompt = input(f"Enter Y after {action_description} to continue: ")

        # Give time to switch windows
        wait_time = 5
        for i in range(wait_time, 0, -1):
            print("Switch back to the TikTok window.")
            print(f"Beginning in: {i}s...")
            time.sleep(1)
        print(f"Beginning interaction...")
        
    def _promptCaptcha(self):
        self._promptAction("completing captcha")
            
    def _checkElementExists(self, element_id):
        if len(self.driver.find_elements(By.ID, element_id)) > 0:
            return True
        else:
            return False
        
    def _checkForCapcha(self):
        if self._checkElementExists("captcha-verify-container-main-page"):
            self._promptCaptcha()
    
    def _get_active_element(self, css_selector):
        """
        Calculates which element is closest to the center of the user's screen.
        Essential for infinite scroll feeds where multiple items exist in the DOM.
        """
        # 1. Get current Viewport geometry
        viewport_height = self.driver.execute_script("return window.innerHeight")
        scroll_y = self.driver.execute_script("return window.scrollY")
        center_y = viewport_height / 2
        
        # 2. Find ALL matches in the DOM
        elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
        
        best_element = None
        min_distance = float('inf') # Start with infinity

        for element in elements:
            try:
                # 3. Calculate position relative to the VIEWPORT, not the document
                # element.location['y'] = Position in total document
                # scroll_y = How much we have scrolled down
                relative_y = element.location['y'] - scroll_y
                
                # We find the center of the element to be precise
                element_center = relative_y + (element.size['height'] / 2)
                
                # How far is this element from the center of the screen?
                distance = abs(center_y - element_center)
                
                # If this is the closest one so far, save it
                if distance < min_distance:
                    min_distance = distance
                    best_element = element
            except:
                continue

        if best_element:
            return best_element
        
        raise Exception(f"No active element found for selector: {css_selector}")
    
    def getUrl(self):
        self._rightClickActiveVideo()
        time.sleep(0.1)  # wait for context menu to appear
        link_element = self.driver.find_element(By.CSS_SELECTOR, "a[href*='is_from_webapp=1']")
        full_url = link_element.get_attribute("href")
        clean_url = full_url.split('?')[0]
        self._pressEsc()
        return clean_url

    def pressLikeButton(self):
        self._checkForCapcha()
        try:
            # Find the HTML element with the aria-label starting with "Like video" (like button)
            like_button = self._get_visible_element("button[aria-label^='Like video']")
            
            # Click the button
            like_button.click()
            print("Liked the video")
            
        except Exception as e:
            print(f"\n\nFAILED: Could not find or could not click the like button.\n\nError: {e}")
            
    def pressSaveButton(self):
        self._checkForCapcha()
        try:
            # Find the HTML element with the aria-label starting with "Add to Favorites." (save button)
            save_button = self._get_visible_element("button[aria-label^='Add to Favorites.']")

            # Click the button
            save_button.click()
            print("Saved the video")
            
        except Exception as e:
            print(f"\n\nFAILED: Could not find or could not click the save button.\n\nError: {e}")
            
    def scroll(self):
        self._checkForCapcha()
        # Simulate down arrow keypress
        self.driver.find_element(By.TAG_NAME, "html").send_keys(Keys.ARROW_DOWN)
        print("Scrolled down")

    def quit(self):
        # Close the browser window
        print("Closing window.")
        self.driver.quit()
