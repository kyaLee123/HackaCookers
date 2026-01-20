import time
import matplotlib.pyplot as plt
import statistics
import csv
import math
import io
import base64

from helper import scraper
from captionBias import Relatedness
from tiktok_webdriver import tiktokWebdriver
from clip_classifier import ClipClassifier

def genericRunner():
    global c, abstractness, reverse_bias_mode


    # Initialize CLIP Classifier


    # --- WAIT FOR TARGET + GO (from HUD) ---
    print("Waiting for you to type a Target in the HUD and press GO...")

    while True:
        hud_state = webdriver.driver.execute_script("""
            return {
                go: window.__HUD_GO_PRESSED__ === true,
                val: window.__HUD_TARGET__,
                absVal: window.__HUD_ABSTRACT__,
                mode: window.__HUD_MODE__
            };
        """)

        if hud_state and hud_state.get("go") and hud_state.get("val") and hud_state.get("absVal") is not None:
            try:
                abs_val = float(hud_state["absVal"])
            except (TypeError, ValueError):
                abs_val = None

            mode = (hud_state.get("mode") or "").strip().lower()

            if abs_val is not None and 0.0 <= abs_val <= 1.0 and mode in ("enhance", "reduce"):
                target_word = str(hud_state["val"]).strip()
                abstractness = abs_val
                reverse_bias_mode = (mode == "reduce")   # reduce = break bias (invert)
                break




    # Now that GO is pressed, set concept + other settings
    c = Relatedness(target_word)
    print("Initializing CLIP Classifier...")
    classifier = ClipClassifier()



    
    i = 0
    while True:
        # Save the data
        if len(scores) % SAVE_EVERY == 0:
            saveImg(fig)
            print(f"Saved Data!")
        


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

        print("getting url...")
        
        while True:
            # get url and scrape
            try:
                url = webdriver.getUrl()
                print(f"Succeed! {url}")
                try:
                    s.getInfo(url, False)
                    break
                except Exception:
                    print("❌URL scraping error❌")
                    webdriver.scroll()
                    time.sleep(1.5)
            except Exception:
                print("❌Fail❌")
                input("URL grab failed, pause the video then press Enter to try again...")
        
        # --- BIAS SCORING ----
        score = c.biasScore(s.description)
        print(f"score: {score}")

        # --- COMBINE SCORES ---
        # Formula: ((Text Score * abstractness weight) + (Visual Score * abstractness weight))
        concrete_weight = [0.3, 0.7] # format: [text weight, visual weight]
        abstract_weight = [0.8, 0.2] # more weight to text for abstract concepts
        score_multipliers = lerp(concrete_weight, abstract_weight, abstractness) # adds up to 1.0
        print(f"Text Score: {score:.3f}, Visual Score: {score_visual:.3f}")
        
        # Save raw scores for display
        raw_text_score = score
        raw_visual_score = score_visual
        
        score = score * score_multipliers[0]
        score_visual = score_visual * score_multipliers[1]
        print(f"Text impact: {(score/1):.3f}%, Visual impact: {(score_visual/1):.3f}%")
        score = (score + score_visual)
        
        # Override: If visual score is very high, trust it regardless of text
        concrete_threshold = [0.8]
        abstract_threshold = [0.95]
        score_visual_threshold = lerp(concrete_threshold, abstract_threshold, abstractness)[0] * score_multipliers[1]
        if score_visual >= score_visual_threshold:
            print(f"Visual Score >= {score_visual_threshold}! Overriding to ensure watch.")
            score = score_visual / score_multipliers[1]  # reverse the multiplier to get full score
            
        print(f"Combined Score: {score:.3f}")

        # Keep a copy of the raw "relevance" score for the graph
        display_score = score
        interaction_score = score

        # --- REVERSE BIAS LOGIC ---
        if reverse_bias_mode:
            print(f"Reverse Mode: Inverting score {score:.3f} -> {1.0-score:.3f}")
            interaction_score = 1.0 - score
        
        # -- DECISION MAKING ----
        interactFullModel(i, interaction_score)
            
        # pause to allow time to scroll/load
        time.sleep(2)
        
        # ----- GRAPH UPDATE -----
        # Always plot the "Relevance" (display_score), not the inverted interaction score
        # This way, if cars disappear, the line goes DOWN.
        liked_this_round = interaction_score > 0.3 # Re-calculate 'liked' based on what we actually did
        updateGraph(i, display_score, liked_this_round)

        # --- UPDATE UI OVERLAY ---
        graph_img = get_graph_base64(fig)
        status = "Analyzing..."
        if liked_this_round:
            status = "✨ Engaging (Biasing)" if not reverse_bias_mode else "⚠️ Breaking Bias"
        else:
            status = "❌ Ignoring"
            
        webdriver.update_overlay(
            target_word=c.word,
            text_score=raw_text_score,
            visual_score=raw_visual_score,
            combined_score=display_score,
            status_text=status,
            graph_base64=graph_img,
            is_reverse_mode=reverse_bias_mode
        )
        
def lerp(start_dist, end_dist, t):
    """
    Linear Interpolation between two distributions.
    t: value between 0 and 1
    """
    return [s + (e - s) * t for s, e in zip(start_dist, end_dist)]
    
def interactFullModel(i, score):
    # -- DECISION MAKING ----
    concrete_threshold = 0.45
    abstract_threshold = 0.2
    concrete_steepness = 1.7
    abstract_steepness = 1.2
    max_watchtime = 25.0
    concrete_like_threshold = 0.7
    abstract_like_threshold = 0.5
    concrete_save_threshold = 0.9
    abstract_save_threshold = 0.75
    
    threshold = lerp([concrete_threshold], [abstract_threshold], abstractness)[0]
    steepness = lerp([concrete_steepness], [abstract_steepness], abstractness)[0]
    like_threshold = lerp([concrete_like_threshold], [abstract_like_threshold], abstractness)[0]
    save_threshold = lerp([concrete_save_threshold], [abstract_save_threshold], abstractness)[0]
    
    liked = score > threshold
    if liked:
        if score > save_threshold:
            print("Saving Video")
            webdriver.pressSaveButton()
            time.sleep(1)  # brief pause for latency
            
        if score > like_threshold:
            print("Liking Video")
            webdriver.pressLikeButton()
            time.sleep(1)  # brief pause for latency

        watch_time_value = value_to_watchtime(score, threshold, steepness, max_watchtime)
        print(f"Watching for {watch_time_value} seconds...")
        time.sleep(watch_time_value)
        i += 1
    else:
        print("Ignoring Video")
        

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

median_line, = ax.plot([], [], label="Rolling Median", color="red")
ax.legend()

SAVE_EVERY = 10 # How many videos to pass to save the data

# init webdriver
webdriver = tiktokWebdriver.TikTokWebdriverInstance()

# open webdriver
webdriver.openTiktok()
webdriver.promptLogin()
time.sleep(1)


webdriver.driver.execute_script("return document.readyState")
webdriver.inject_overlay()


def get_graph_base64(fig):
    """Converts the matplotlib figure to a base64 string for embedding in HTML"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=False, facecolor='#222')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

genericRunner()