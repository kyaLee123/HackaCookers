import asyncio
import argparse
import random
import csv
import re
import time
from datetime import datetime
from playwright.async_api import async_playwright
from playwright._impl._errors import TargetClosedError
from helper.scraper import Scraper
from helper.bias import Concept


# --- CONFIGURATION ---
DATA_FILE = "experiment_data.csv"


# --- PERSONA DEFINITIONS ---
class Persona:
    def __init__(self, name):
        self.name = name


    async def act(self, page, is_target, metadata):
        """
        Execute actions on the current video based on whether it matches the target concept.
        Returns a dictionary of actions taken for logging.
        """
        raise NotImplementedError


class PassivePersona(Persona):
    def __init__(self):
        super().__init__("Passive")


    async def act(self, page, is_target, metadata):
        # Watch 50% of content regardless of target
        print(f"[{self.name}] Watching 50% of video...")
        # Simulating watch time - we don't know duration easily without scraping,
        # but Scraper might give us info or we assume avg length of 15s -> 7.5s wait
        await asyncio.sleep(5)
        return {"action": "watch_partial", "liked": False, "followed": False}


class WatchOnlyPersona(Persona):
    def __init__(self):
        super().__init__("WatchOnly")


    async def act(self, page, is_target, metadata):
        actions = {"liked": False, "followed": False, "shared": False}
       
        if is_target:
            print(f"[{self.name}] TARGET FOUND! Executing 'Rabbit Hole' behavior.")
            # 1. Watch 100% (Simulated 15s)
            await asyncio.sleep(15)
           
            # 2. Re-watch (Loop)
            print(f"[{self.name}] Re-watching...")
            await asyncio.sleep(15)
           
            # 3. Pause (Hover/Click)
            print(f"[{self.name}] Pausing to linger...")
            # Try to click video to pause/play
            try:
                await page.locator("[data-e2e='video-card']").first.click()
                await asyncio.sleep(3)
                await page.locator("[data-e2e='video-card']").first.click() # Resume
            except:
                pass
           
            actions["action"] = "watch_full_rewatch_pause"
        else:
            print(f"[{self.name}] Non-target. Skipping.")
            await asyncio.sleep(1) # Skip quickly
            actions["action"] = "skip"
           
        return actions


class ActivePersona(Persona):
    def __init__(self):
        super().__init__("Active")


    async def act(self, page, is_target, metadata):
        actions = {"liked": False, "followed": False, "shared": False}
       
        if is_target:
            print(f"[{self.name}] TARGET FOUND! Engaging.")
            # Watch 100%
            await asyncio.sleep(15)
           
            # Like
            try:
                await page.locator("[data-e2e='like-icon']").first.click()
                print(f"[{self.name}] Liked.")
                actions["liked"] = True
            except Exception as e:
                print(f"Error liking: {e}")


            # Follow (33% chance)
            if random.random() < 0.33:
                try:
                    await page.locator("[data-e2e='video-follow']").first.click()
                    print(f"[{self.name}] Followed.")
                    actions["followed"] = True
                except:
                    pass


            # Share (20% chance)
            if random.random() < 0.20:
                try:
                    await page.locator("[data-e2e='share-icon']").first.click()
                    print(f"[{self.name}] Shared.")
                    actions["shared"] = True
                except:
                    pass
           
            actions["action"] = "engage_full"
        else:
            print(f"[{self.name}] Non-target. Skipping.")
            await asyncio.sleep(1)
            actions["action"] = "skip"
           
        return actions


# --- MAIN BOT LOOP ---
async def run_bot(persona_name, concept_text):
    print(f"Starting Bot with Persona: {persona_name} | Concept: {concept_text}")
   
    # Initialize helpers
    scraper = Scraper()
    concept = Concept(concept_text)
   
    # Select Persona
    if persona_name.lower() == "passive":
        persona = PassivePersona()
    elif persona_name.lower() == "watchonly":
        persona = WatchOnlyPersona()
    elif persona_name.lower() == "active":
        persona = ActivePersona()
    else:
        raise ValueError("Invalid persona. Choose: passive, watchonly, active")


    # Setup Playwright
    async with async_playwright() as p:
        # Launch persistent context to save login session
        user_data_dir = "user_data_dir_clean"
        print(f"Launching browser with persistent profile in '{user_data_dir}'...")
       
        browser_context = None
        try:
            browser_context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False, # Must be visible for TikTok
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 720}
            )
           
            page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
           
            # Anti-detect script
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)


            print("Navigating to TikTok...")
            await page.goto("https://www.tiktok.com/foryou", timeout=60000)


            print("\nIMPORTANT: If you are not logged in, please log in now.")
            print("Tip: If you see 'Maximum attempts reached', wait a while or try a different account.")
            input("Press Enter once you are effectively logged in and ready to start...")
           
            video_count = 0
           
            # Prepare CSV
            with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Header if new file
                if f.tell() == 0:
                    writer.writerow(["timestamp", "video_id", "author", "persona", "is_target", "bias_score", "action", "liked", "followed", "transcript_snippet"])


                while True:
                    video_count += 1
                    print(f"\n--- Processing Video #{video_count} ---")
                
                    # Get current video URL
                    current_url = "https://www.tiktok.com/foryou" # Default fallback
                    try:
                        # Strategy 1: Check browser URL first (most reliable if it updates)
                        if "/video/" in page.url:
                            current_url = page.url
                            print(f"[DEBUG] Found URL from browser address bar: {current_url}")
                        else:
                            print("[DEBUG] Browser URL is generic. Searching DOM for active video...", end=" ")
                        
                            # Strategy 2: visual-based (center of screen) + multiple fallback selectors
                            current_url = await page.evaluate("""() => {
                                // Helper to check if element is in view (center of screen)
                                function isInView(el) {
                                    if (!el) return false;
                                    const rect = el.getBoundingClientRect();
                                    const windowHeight = (window.innerHeight || document.documentElement.clientHeight);
                                    const windowWidth = (window.innerWidth || document.documentElement.clientWidth);
                                
                                    // Check if the element 'center' is in the viewport
                                    const elementCenterX = rect.left + rect.width / 2;
                                    const elementCenterY = rect.top + rect.height / 2;


                                    return (
                                        elementCenterY >= 0 &&
                                        elementCenterY <= windowHeight &&
                                        elementCenterX >= 0 &&
                                        elementCenterX <= windowWidth
                                    );
                                }


                                // 1. Find the active container
                                const containers = document.querySelectorAll('article[data-e2e="recommend-list-item-container"]');
                                let activeContainer = null;
                            
                                for (const container of containers) {
                                    if (isInView(container)) {
                                        activeContainer = container;
                                        break; // Found the focused one
                                    }
                                }


                                if (!activeContainer) {
                                    // Fallback: try finding *any* video wrapper in view
                                    const wrappers = document.querySelectorAll('div[id^="xgwrapper-"]');
                                    for (const wrapper of wrappers) {
                                        if (isInView(wrapper)) {
                                            // Found a wrapper, try to find its container
                                            activeContainer = wrapper.closest('article[data-e2e="recommend-list-item-container"]');
                                            if (activeContainer) break;
                                        
                                            // If no container (unlikely), try to extract just from wrapper
                                            const idParts = wrapper.id.split('-');
                                            const videoId = idParts[idParts.length - 1];
                                            return `https://www.tiktok.com/video/${videoId}`; // Partial URL might work for yt-dlp
                                        }
                                    }
                                }


                                if (activeContainer) {
                                    // EXTRACT VIDEO ID
                                    const videoWrapper = activeContainer.querySelector('div[id^="xgwrapper-"]');
                                    let videoId = null;
                                    if (videoWrapper) {
                                        const idParts = videoWrapper.id.split('-');
                                        videoId = idParts[idParts.length - 1];
                                    }


                                    // EXTRACT AUTHOR - This is needed for the proper URL format
                                    const authorLink = activeContainer.querySelector('a[data-e2e="video-author-avatar"]');
                                    let author = null;
                                    if (authorLink) {
                                        // href is usually /@username
                                        const href = authorLink.getAttribute('href');
                                        if (href) {
                                            author = href.startsWith('/') ? href.substring(1) : href;
                                        }
                                    }


                                    // CONSTRUCT URL
                                    if (videoId && author) {
                                        return `https://www.tiktok.com/${author}/video/${videoId}`;
                                    } else if (videoId) {
                                        return `https://www.tiktok.com/video/${videoId}`;
                                    }
                                
                                    // Fallback: Look for any link with /video/ in the container
                                    const links = activeContainer.querySelectorAll('a');
                                    for (const link of links) {
                                        if (link.href.includes('/video/')) {
                                            return link.href;
                                        }
                                    }
                                }


                                return window.location.href;
                            }""")
                        
                            if "/video/" in current_url:
                                print(f"Success! Found via DOM: {current_url}")
                            else:
                                print("Failed.")


                        # Strategy 3: Playwright Level Selector Fallback (if JS evaluation failed to return specific)
                        if "foryou" in current_url:
                            print("[DEBUG] JS evaluation failed. Trying Playwright locators...")
                            # Sometimes the 'video-desc' selector is a good anchor usage
                            try:
                                # Get the first visible video desc -> navigate up/around to find link
                                # This assumes the first one is the active one, which often holds true on scroll
                                possible_link = await page.locator("[data-e2e='recommend-list-item-container'] a").first.get_attribute("href")
                                if possible_link and "/video/" in possible_link:
                                    current_url = possible_link
                                    if not current_url.startswith("http"):
                                        current_url = "https://www.tiktok.com" + current_url
                                    print(f"[DEBUG] Found via Playwright locator fallback: {current_url}")
                            except Exception as play_e:
                                print(f"[DEBUG] Playwright locator fallback failed: {play_e}")


                    except Exception as e:
                        print(f"[ERROR] Extraction logic crashed: {e}")
                    
                    if "foryou" in current_url:
                        print(f"[ERROR] Could not detect video URL. Dumping HTML for debugging...")
                    
                        # Generate debug dump
                        timestamp = int(time.time())
                        filename = f"debug_failed_detect_{timestamp}.html"
                        try:
                            content = await page.content()
                            # import os (already imported in loop but good practice to move up, I will move imports to top)
                            with open(filename, "w", encoding="utf-8") as f:
                                f.write(content)
                            print(f"[DEBUG] Saved page HTML to {filename}")
                        except Exception as dump_e:
                            print(f"[ERROR] Failed to save debug HTML: {dump_e}")


                        print("Skipping scrape for this iteration and scrolling...")
                        time.sleep(2)
                        await page.keyboard.press("ArrowDown")
                        continue


                    print(f"URL: {current_url}")
                
                    # 1. Scrape
                    print("Scraping data...")
                    # Note: scraper.getInfo downloads audio. This takes time.
                    try:
                        title, description, channel, transcript = scraper.getInfo(current_url)
                    except Exception as e:
                        print(f"[WARN] Scraping failed with yt-dlp: {e}")
                        print("[INFO] Attempting fallback DOM extraction for description...")
                        try:
                            # Fallback: Extract basic info from DOM
                            description = await page.evaluate("""() => {
                                // Try common description selectors
                                const descEl = document.querySelector('[data-e2e="video-desc"]');
                                return descEl ? descEl.innerText : "";
                            }""")
                        
                            channel = await page.evaluate("""() => {
                                const authorEl = document.querySelector('[data-e2e="video-author-uniqueid"]');
                                return authorEl ? authorEl.innerText : "unknown";
                            }""")
                        
                            title = description[:30] if description else "Unknown Title"
                            transcript = "" # Cannot get transcript without scraping
                        
                            print(f"[INFO] Fallback successful. Desc: {description[:30]}...")
                        except Exception as fallback_e:
                            print(f"[ERROR] Fallback extraction failed: {fallback_e}")
                            print("Skipping video due to total extraction failure.")
                            await page.keyboard.press("ArrowDown")
                            await asyncio.sleep(2)
                            continue


                    # 2. Score Bias
                    # Clean up text components, handling None
                    clean_desc = description if description else ""
                    clean_trans = transcript if transcript else ""
                    full_text = f"{clean_desc} {clean_trans}".strip()
                
                    if not full_text:
                        print("[DEBUG] No text content found (empty desc & transcript). Score defaulting to 0.")
                        score = 0.0
                        is_target = False
                    else:
                        # Print preview of what we are scoring
                        preview_text = full_text[:100].replace('\n', ' ')
                        print(f"[DEBUG] Scoring Text: '{preview_text}...'")
                    
                        score = concept.biasScore(full_text)
                        is_target = score > 0.15 # Threshold (can be tuned)
                
                    print(f"Score: {score:.3f} | Target: {is_target}")
                    print(f"Desc: {clean_desc[:50]}...")
                
                    # 3. Act
                    action_data = await persona.act(page, is_target, None)
                
                    # 4. Log
                    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            datetime.now(),
                            current_url,
                            channel,
                            persona.name,
                            is_target,
                            score,
                            action_data.get("action"),
                            action_data.get("liked"),
                            action_data.get("followed"),
                            transcript[:50] if transcript else ""
                        ])
                
                    # 5. Move to next
                    print("Moving to next video...")
                    await page.keyboard.press("ArrowDown")
                    await asyncio.sleep(2) # Wait for scroll animation

        except TargetClosedError:
            print("\n[INFO] Browser was closed. Stopping bot.")
        except KeyboardInterrupt:
            print("\n[INFO] Bot stopped by user.")
        except Exception as e:
            print(f"\n[ERROR] Unexpected crash: {e}")
        finally:
             if browser_context:
                 await browser_context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("persona", help="passive, watchonly, or active")
    parser.add_argument("concept", help="Target concept (e.g., 'cooking', 'gaming')")
    args = parser.parse_args()
   
    asyncio.run(run_bot(args.persona, args.concept))
