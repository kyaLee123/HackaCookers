from tiktok_webdriver import tiktokWebdriver
import time
import captionBias   # ← change ONLY this import


from helper import scraper

s = scraper.Scraper()
c = captionBias.Concept("dance")   # ← SAME call as before

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