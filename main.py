from tiktok_webdriver import tiktokWebdriver
import time
import captionBias


from helper import scraper

s = scraper.Scraper()
c = captionBias.Concept("dance")

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
        print(f"Sucessfully grabbed URL: {url}")
    except Exception:
        print("Failed!")
        s.description = "bob"

    score = c.biasScore(s.description)

    print(f"score: {score}")

    if (c.biasScore(s.description) > 0.5):
        print("Like (waiting 20s)...")
        time.sleep(20)
    else:
        print("Ignore")

    time.sleep(1)

    webdriver.scroll()

    # pause for dramatic effect
    time.sleep(2)