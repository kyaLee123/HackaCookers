from tiktok_webdriver import tiktokWebdriver
import time

from helper import scraper
from helper import bias

s = scraper.Scraper()
c = bias.Concept("dance")

webdriver = tiktokWebdriver.TikTokWebdriverInstance()

# open 
webdriver.openTiktok()
webdriver.promptLogin()
time.sleep(1)

while True:
    url = webdriver.getUrl()
    try:
        s.getInfo(url, False)
    except Exception:
        s.description = "bob"

    score = c.biasScore(s.description)

    if (c.biasScore(s.description) > 0.5):
        time.sleep(10)
        print("Like")
    else:
        print("Ignore")

    print(f"score: {score}")

    time.sleep(1)

    webdriver.scroll()

    # pause for dramatic effect
    time.sleep(2)