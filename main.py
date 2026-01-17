import time
import matplotlib.pyplot as plt
import statistics
import csv

from helper import scraper
from captionBias import Relatedness
from tiktok_webdriver import tiktokWebdriver
from clip_classifier import ClipClassifier

# Set to True to run the full interaction model (likes, saves)
# Set to False if you want to test w/o logging in
run_full_model = False

def genericRunner():
    # Initialize CLIP Classifier
    print("Initializing CLIP Classifier...")
    classifier = ClipClassifier()
    
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

        # --- VISUAL CLASSIFICATION ---
        # 1. Capture Screenshot
        screenshot_path = "temp_screenshot.jpg"
        if webdriver.capture_screenshot(screenshot_path):
            # 2. Classify
            labels = [c.word, "irrelevant"] # Concept vs Irrelevant
            result = classifier.classify(screenshot_path, labels)
            
            if result:
                top_label = result["top_label"]
                # Visual score is the probability of the concept label
                # We map back from the label string to the score in result["all_scores"]
                score_visual = result["all_scores"].get(labels[0], 0.0)
                print(f"Visual Classification: {top_label} (Score: {score_visual:.3f})")
            else:
                print("Visual classification failed.")
                score_visual = 0.0
        else:
            print("Screenshot failed, skipping visual classification.")
            score_visual = 0.0

        # --- COMBINE SCORES ---
        # Formula: (Text Score + Visual Score) / 2
        # If one is 0, it drags the other down, which is good for safety? 
        # Or should we only average non-zeroes? 
        # User agreed to simple average.
        print(f"Text Score: {score:.3f}, Visual Score: {score_visual:.3f}")
        score = (score + score_visual) / 2
        print(f"Combined Score: {score:.3f}")


        
        # -- DECISION MAKING ----
        # run relevant decision function
        if run_full_model:
            interactFullModel(i, score)
        else:
            interactAsTest(i, score)

def interactAsTest(i, score):
    # -- DECISION MAKING ----
    liked = score > 0.5
    if liked:
        time.sleep(20)
        i += 1
        print("Liking Video")
    else:
        print("Ignoring Video")
        
    # ----- GRAPH UPDATE -----
    updateGraph(i, score, liked)
    
    
    time.sleep(1)
    webdriver.scroll()
    # pause for dramatic effect
    time.sleep(2)

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