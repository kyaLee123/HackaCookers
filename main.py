import time
import matplotlib.pyplot as plt
import statistics

from helper import scraper
from captionBias import Relatedness
from tiktok_webdriver import tiktokWebdriver

# Matplotlib stuff
plt.ion()
fig, ax = plt.subplots()

scores = []
likes = []

line, = ax.plot([], [], marker="o", label="Bias Score")
like_line, = ax.plot([], [], "o", label="Liked")

ax.set_ylim(0, 1)
ax.set_xlabel("Video #")
ax.set_ylabel("Bias Score")
ax.set_title("TikTok Bias Over Time")
ax.legend()

WINDOW = 15   # how many recent videos to smooth over

median_line, = ax.plot([], [], linestyle="--", label="Rolling Median")
ax.legend()

s = scraper.Scraper()
c = Relatedness("dance")

webdriver = tiktokWebdriver.TikTokWebdriverInstance()

# open 
webdriver.openTiktok()
webdriver.promptLogin()
time.sleep(1)

i = 0
while True:
    print("getting url...")
    try:
        url = webdriver.getUrl()
        s.getInfo(url, False)
        print(f"Succeed! {url}")
    except Exception:
        print("Fail!")
        s.description = "bob"
    score = c.biasScore(s.description)
    print(f"score: {score}")
    liked = score > 0.5
    if liked:
        time.sleep(20)
        i += 1
        print("Liking Video")
    else:
        print("Ignoring Video")
    # ----- GRAPH UPDATE -----
    scores.append(score)
    likes.append(i if liked else None)
    x = list(range(len(scores)))
    line.set_data(x, scores)
    # liked points
    like_x = [j for j, v in enumerate(likes) if v is not None]
    like_y = [scores[j] for j in like_x]
    like_line.set_data(like_x, like_y)
    # rolling median
    med_x = []
    med_y = []
    for j in range(len(scores)):
        start = max(0, j - WINDOW + 1)
        window_vals = scores[start:j+1]
        med_x.append(j)
        med_y.append(statistics.median(window_vals))
    median_line.set_data(med_x, med_y)
    ax.set_xlim(0, len(scores))
    fig.canvas.draw()
    fig.canvas.flush_events()
    # -------------------------
    time.sleep(1)
    webdriver.scroll()
    # pause for dramatic effect
    time.sleep(2)