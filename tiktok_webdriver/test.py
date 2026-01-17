from tiktok_webdriver import tiktokWebdriver
import time

webdriver = tiktokWebdriver.TikTokWebdriverInstance()

# open 
webdriver.openTiktok()
webdriver.promptLogin()
# test functionality
webdriver.scroll()
time.sleep(2)
webdriver.pressSaveButton()
time.sleep(1)
webdriver.pressLikeButton()
# pause for dramatic effect
time.sleep(4)
# quit
webdriver.quit()