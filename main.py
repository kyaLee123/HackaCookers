from tiktok_webdriver import tiktokWebdriver
import time

from helper import scraper
from helper import bias

s = scraper.Scraper()
c = bias.Concept("dog")

webdriver = tiktokWebdriver.TikTokWebdriverInstance()

# open 
webdriver.openTiktok()
webdriver.promptLogin()
time.sleep(1)

while True:
    print("getting url...")
    try:
        url = webdriver.getUrl()
        s.getInfo(url, False)
        print(f"Succeed! {url}")
    except Exception:
        print("Failed!")
        s.description = "bob"

    score = c.biasScore(s.description)

    if (c.biasScore(s.description) > 0.5):
        time.sleep(20)
        print("Like")
    else:
        print("Ignore")

    print(f"score: {score}")

    time.sleep(1)

    webdriver.scroll()

    # pause for dramatic effect
    time.sleep(2)