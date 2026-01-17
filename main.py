import time
import matplotlib.pyplot as plt
import statistics
import csv
import math

from helper import scraper
from captionBias import Relatedness
from tiktok_webdriver import tiktokWebdriver

# Set to True to run the full interaction model (likes, saves)
# Set to False if you want to test w/o logging in
run_full_model = False

def genericRunner():
    i = 0
    while True:
        # Save the data
        if len(scores) % SAVE_EVERY == 0:
            saveImg(fig)
            print(f"Saved Data!")
        print("getting url...")
        
        # get url and scrape
        try:
            url = webdriver.getUrl()
            s.getInfo(url, False)
            print(f"Succeed! {url}")
        except Exception:
            print("Fail!")
            s.description = "bob"
        
        # --- BIAS SCORING ----
        score = c.biasScore(s.description)
        print(f"score: {score}")
        
        # -- DECISION MAKING ----
        # run relevant decision function
        if run_full_model:
            interactFullModel(i, score)
        else:
            interactAsTest(i, score)
            
        # pause to allow time to scroll/load
        time.sleep(2)

def interactAsTest(i, score):
    # -- DECISION MAKING ----
    liked = score > 0.5
    if liked:
        watch_time_value = value_to_watchtime(score, 0.3, 1.5, 30.0)
        print(f"Watching for {watch_time_value} seconds...")
        time.sleep(watch_time_value)
        i += 1
    else:
        print("Ignoring Video")
        
    # ----- GRAPH UPDATE -----
    updateGraph(i, score, liked)
    
    webdriver.scroll()
    
def value_to_watchtime(bias_value: float, threshold: float, steepness: float, max_waittime: float) -> float:
    """
    Maps an input value (within [threshold, 1.0]) to an output [0, max_waittime] 
    using an exponential curve.
    
    Args:
        value: The input value to map.
        threshold: The lower bound of the input range. 
                   Values below this return 0.
        steepness: Controls curvature. 
                   > 0 is convex (starts slow), < 0 is concave (starts fast).
        max_value: The maximum output value when input is 1.0.
    """
    # Safety check to avoid division by zero if threshold is 1.0
    if threshold >= 1.0:
        return 0.0 if bias_value < 1.0 else max_waittime

    # Clamp the input so it doesn't go outside [threshold, 1.0]
    #    This ensures we don't get negative outputs or overshoot max_value.
    clamped_value = max(threshold, min(1.0, bias_value))

    # Normalize the input to a 0.0 - 1.0 range (t)
    #    Example: If threshold is 0.5 and input is 0.75, t becomes 0.5.
    t = (clamped_value - threshold) / (1.0 - threshold)

    # Handle linear case (steepness approx 0)
    if abs(steepness) < 1e-6:
        return t * max_waittime

    # Apply the exponential formula
    #    f(t) = (e^(k*t) - 1) / (e^k - 1)
    curve = (math.exp(steepness * t) - 1) / (math.exp(steepness) - 1)

    return curve * max_waittime

def interactFullModel():
    return 0

def saveImg(fig, filename="bias_plot.png"):
    fig.savefig(filename, dpi=200, bbox_inches="tight")
    
def updateGraph(i, score, liked):
    global scores, likes
    
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

# Initialize scraper and concept
s = scraper.Scraper()
c = Relatedness(input("Enter concept word: "))

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

SAVE_EVERY = 10 # How many videos to pass to save the data

# init webdriver
webdriver = tiktokWebdriver.TikTokWebdriverInstance()

# open webdriver
webdriver.openTiktok()
webdriver.promptLogin()


genericRunner()