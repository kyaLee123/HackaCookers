from tiktok_webdriver import tiktokWebdriver
import time

webdriver = tiktokWebdriver.TikTokWebdriverInstance()

# open 
webdriver.openTiktok()
webdriver.promptLogin()
time.sleep(1)
print(f"Video URL: {webdriver.getUrl()}")


# test functionality
time.sleep(1)
webdriver.scroll()
time.sleep(2)
webdriver.pressLikeButton()
#time.sleep(1)
#webdriver.pressSaveButton()



# pause for dramatic effect
time.sleep(4)
# quit
webdriver.quit()