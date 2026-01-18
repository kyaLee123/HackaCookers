from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TikTokWebdriverInstance:  # _ indicates internal use
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        print("open your chrome tab through the terminal with:")
        print(
            '(mac)\n/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome-profile"'
        )
        print(
            '(windows)\n"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\selenium\\ChromeProfile"'
        )
        input("And then press Enter to continue...")

        self.driver = webdriver.Chrome(options=chrome_options)

    def openTiktok(self):
        self.driver.get("https://www.tiktok.com/en/")

    def promptLogin(self):
        print("(Remember to right press & click 'view video details' after logging in).")
        self._promptAction("logging in to tiktok")

    def _promptAction(self, action_description):
        continue_prompt = ""
        while continue_prompt.lower() != "y":
            continue_prompt = input(f"Enter Y after {action_description} to continue: ")

        wait_time = 5
        for i in range(wait_time, 0, -1):
            print("Switch back to the TikTok window.")
            print(f"Beginning in: {i}s...")
            time.sleep(1)
        print("Beginning interaction...")

    def _promptCaptcha(self):
        self._promptAction("completing captcha")

    def _checkElementExists(self, element_id):
        return len(self.driver.find_elements(By.ID, element_id)) > 0

    def _checkForCapcha(self):
        if self._checkElementExists("captcha-verify-container-main-page"):
            self._promptCaptcha()

    def _get_visible_element(self, css_selector):
        viewport_height = self.driver.execute_script("return window.innerHeight")
        elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
        for element in elements:
            try:
                y_position = element.location["y"]
                if 0 < y_position < viewport_height:
                    return element
            except:
                continue
        raise Exception("No visible element found in viewport")

    def _get_active_element(self, css_selector):
        viewport_height = self.driver.execute_script("return window.innerHeight")
        scroll_y = self.driver.execute_script("return window.scrollY")
        center_y = viewport_height / 2

        elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)

        best_element = None
        min_distance = float("inf")
        for element in elements:
            try:
                relative_y = element.location["y"] - scroll_y
                element_center = relative_y + (element.size["height"] / 2)
                distance = abs(center_y - element_center)
                if distance < min_distance:
                    min_distance = distance
                    best_element = element
            except:
                continue

        if best_element:
            return best_element
        raise Exception(f"No active element found for selector: {css_selector}")

    def getUrl(self):
        try:
            active_container = self._get_active_element("[data-e2e='recommend-list-item-container']")

            video_id = None
            try:
                video_wrapper = active_container.find_element(By.CSS_SELECTOR, 'div[id^="xgwrapper-"]')
                wrapper_id = video_wrapper.get_attribute("id")
                video_id = wrapper_id.split("-")[-1]
            except:
                pass

            author = None
            try:
                author_link = active_container.find_element(By.CSS_SELECTOR, 'a[data-e2e="video-author-avatar"]')
                href = author_link.get_dom_attribute("href")
                if href:
                    author = href.lstrip("/") if href.startswith("/") else href
            except:
                pass

            if video_id and author:
                return f"https://www.tiktok.com/{author}/video/{video_id}"
            elif video_id:
                return f"https://www.tiktok.com/video/{video_id}"
            return None

        except Exception as e:
            print(f"FAILED: URL construction error: {e}")
            return None

    def pressLikeButton(self):
        self._checkForCapcha()
        try:
            like_button = self._get_visible_element("button[aria-label^='Like video']")
            like_button.click()
            print("Liked the video")
        except Exception as e:
            print(f"\n\nFAILED: Could not find or click the like button.\n\nError: {e}")

    def pressSaveButton(self):
        self._checkForCapcha()
        try:
            save_button = self._get_visible_element("button[aria-label^='Add to Favorites.']")
            save_button.click()
            print("Saved the video")
        except Exception as e:
            print(f"\n\nFAILED: Could not find or click the save button.\n\nError: {e}")

    def scroll(self):
        self._checkForCapcha()
        self.driver.find_element(By.TAG_NAME, "html").send_keys(Keys.ARROW_DOWN)
        print("Scrolled down")

    def quit(self):
        print("Closing window.")
        self.driver.quit()

    def capture_screenshot(self, filename="screenshot.jpg"):
        try:
            active_container = self._get_active_element("[data-e2e='recommend-list-item-container']")
            video_element = active_container.find_element(By.TAG_NAME, "video")
            video_element.screenshot(filename)
            print(f"Video element screenshot saved to {filename}")
            return True
        except Exception as e:
            print(f"Failed to capture video element screenshot: {e}")
            try:
                self.driver.save_screenshot(filename)
                print(f"Full page screenshot saved to {filename} (fallback)")
                return True
            except Exception as e2:
                print(f"Failed to capture fallback screenshot: {e2}")
                return False

    def getVideoDescription(self):
        try:
            active_container = self._get_active_element("[data-e2e='recommend-list-item-container']")
            try:
                desc_element = active_container.find_element(By.CSS_SELECTOR, "[data-e2e='video-desc']")
                return desc_element.text
            except:
                return ""
        except Exception as e:
            print(f"Failed to get description: {e}")
            return ""

    # ------------------------------------------------------------------
    # HUD overlay with:
    # - Abstract textbox
    # - Target textbox
    # - Mode radios (Enhance/Reduce)
    # - GO button
    #
    # GO stores:
    #   window.__HUD_TARGET__
    #   window.__HUD_ABSTRACT__
    #   window.__HUD_MODE__          ("enhance" | "reduce")
    #   window.__HUD_GO_PRESSED__    true
    # ------------------------------------------------------------------
    def inject_overlay(self):
        js_code = r"""
        (function () {
            // init globals (once)
            if (window.__HUD_GO_PRESSED__ === undefined) window.__HUD_GO_PRESSED__ = false;
            if (window.__HUD_TARGET__ === undefined) window.__HUD_TARGET__ = "";
            if (window.__HUD_ABSTRACT__ === undefined) window.__HUD_ABSTRACT__ = 0.5;
            if (window.__HUD_MODE__ === undefined) window.__HUD_MODE__ = "enhance";

            if (!document.getElementById('ai-hud')) {
                const hud = document.createElement('div');
                hud.id = 'ai-hud';
                hud.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    width: 350px;
                    background: rgba(0, 0, 0, 0.85);
                    color: #fff;
                    padding: 15px;
                    border-radius: 12px;
                    font-family: 'Proxima Nova', sans-serif;
                    z-index: 10000;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                    border: 1px solid rgba(255,255,255,0.1);
                    backdrop-filter: blur(10px);
                `;

                hud.innerHTML = `
                    <h3 style="margin: 0 0 10px 0; color: #fe2c55; font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 5px;">
                        🤖 AI Bias Monitor
                    </h3>

                    <!-- Abstractness row -->
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom: 10px;">
                        <span style="color:#aaa;">Abstract:</span>
                        <input
                            id="hud-abstract"
                            type="number"
                            inputmode="decimal"
                            value="0.5"
                            min="0"
                            max="1"
                            step="0.05"
                            placeholder="0.0 - 1.0"
                            style="
                                width: 120px;
                                padding: 6px 8px;
                                border-radius: 8px;
                                border: 1px solid #444;
                                background: #111;
                                color: #00f2ea;
                                font-weight: bold;
                                outline: none;
                                text-align: right;
                            "
                        />
                    </div>

                    <!-- Target row -->
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom: 10px;">
                        <span style="color:#aaa;">Target:</span>
                        <input
                            id="hud-target"
                            type="text"
                            value=""
                            placeholder="Type target..."
                            style="
                                width: 220px;
                                padding: 6px 8px;
                                border-radius: 8px;
                                border: 1px solid #444;
                                background: #111;
                                color: #00f2ea;
                                font-weight: bold;
                                outline: none;
                                text-align: right;
                            "
                        />
                    </div>

                    <!-- Mode row (NEW): Enhance vs Reduce (radio, only one can be selected) -->
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom: 10px;">
                        <span style="color:#aaa;">Mode:</span>
                        <div style="display:flex; gap:12px; align-items:center; justify-content:flex-end; flex:1;">
                            <label style="display:flex; gap:6px; align-items:center; cursor:pointer;">
                                <input type="radio" name="hud-mode" id="hud-mode-enhance" value="enhance" checked />
                                <span>Enhance</span>
                            </label>
                            <label style="display:flex; gap:6px; align-items:center; cursor:pointer;">
                                <input type="radio" name="hud-mode" id="hud-mode-reduce" value="reduce" />
                                <span>Reduce</span>
                            </label>

                            <button
                                id="hud-go"
                                style="
                                    margin-left: 6px;
                                    padding: 6px 10px;
                                    border-radius: 8px;
                                    border: 1px solid rgba(255,255,255,0.15);
                                    background: rgba(254,44,85,0.9);
                                    color: #fff;
                                    font-weight: bold;
                                    cursor: pointer;
                                    user-select: none;
                                "
                            >GO</button>
                        </div>
                    </div>

                    <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span>Text Relevance:</span>
                            <span id="hud-text-score" style="color: #00f2ea;">0.00</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span>Visual Relevance:</span>
                            <span id="hud-visual-score" style="color: #00f2ea;">0.00</span>
                        </div>
                        <div style="height: 1px; background: #444; margin: 5px 0;"></div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>Combined Score:</span>
                            <span id="hud-combined-score" style="font-weight: bold; color: #fff;">0.00</span>
                        </div>
                    </div>

                    <div style="margin-bottom: 10px; font-size: 14px;">
                        <span id="hud-status" style="display:block; text-align:center; padding:5px; background:#333; border-radius:4px;">
                            Waiting for Abstract + Target + Mode + GO...
                        </span>
                    </div>

                    <div style="text-align: center;">
                        <img id="hud-graph" style="width: 100%; border-radius: 4px; border: 1px solid #444;" src="" />
                    </div>
                `;

                document.body.appendChild(hud);

                const goBtn = document.getElementById('hud-go');
                const input = document.getElementById('hud-target');
                const absInput = document.getElementById('hud-abstract');
                const status = document.getElementById('hud-status');
                const enhanceRadio = document.getElementById('hud-mode-enhance');
                const reduceRadio = document.getElementById('hud-mode-reduce');

                function getMode() {
                    if (reduceRadio && reduceRadio.checked) return 'reduce';
                    return 'enhance';
                }

                function pressGo() {
                    const targetVal = (input && input.value) ? input.value.trim() : '';
                    const absValRaw = absInput ? (absInput.value || '').trim() : '';
                    const absVal = parseFloat(absValRaw);
                    const mode = getMode();

                    if (!targetVal) {
                        if (status) status.innerText = '⚠️ Enter a target first';
                        return;
                    }
                    if (!Number.isFinite(absVal) || absVal < 0 || absVal > 1) {
                        if (status) status.innerText = '⚠️ Abstract must be 0.0 - 1.0';
                        return;
                    }
                    if (mode !== 'enhance' && mode !== 'reduce') {
                        if (status) status.innerText = '⚠️ Choose Enhance or Reduce';
                        return;
                    }

                    // Store values for Python to read
                    window.__HUD_TARGET__ = targetVal;
                    window.__HUD_ABSTRACT__ = absVal;
                    window.__HUD_MODE__ = mode;
                    window.__HUD_GO_PRESSED__ = true;

                    if (status) status.innerText = '✅ GO pressed. Starting...';

                    // Lock inputs
                    if (input) input.disabled = true;
                    if (absInput) absInput.disabled = true;
                    if (enhanceRadio) enhanceRadio.disabled = true;
                    if (reduceRadio) reduceRadio.disabled = true;
                    if (goBtn) goBtn.disabled = true;
                    if (goBtn) goBtn.style.opacity = '0.6';
                }

                if (goBtn) goBtn.addEventListener('click', pressGo);

                // Enter triggers GO from either textbox
                if (input) input.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter') pressGo();
                });
                if (absInput) absInput.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter') pressGo();
                });

                // Restore any previously stored values (if you reinject)
                try {
                    if (window.__HUD_TARGET__ && input && !input.value) input.value = window.__HUD_TARGET__;
                    if (Number.isFinite(window.__HUD_ABSTRACT__) && absInput) absInput.value = window.__HUD_ABSTRACT__;
                    if (window.__HUD_MODE__ === 'reduce' && reduceRadio) reduceRadio.checked = true;
                } catch (e) {}
            }
        })();
        """
        try:
            self.driver.execute_script(js_code)
            print("HUD Overlay injected.")
        except Exception as e:
            print(f"Failed to inject HUD: {e}")

    # IMPORTANT: update_overlay signature now matches main.py
    # - does NOT overwrite the target textbox once user typed it
    def update_overlay(
        self,
        target_word,
        text_score,
        visual_score,
        combined_score,
        status_text,
        graph_base64,
        is_reverse_mode=False,
    ):
        status_text = (status_text or "").replace("\\", "\\\\").replace("'", "\\'")
        target_word = (target_word or "").replace("\\", "\\\\").replace("'", "\\'")

        mode_color = "#ff0050" if is_reverse_mode else "#00f2ea"

        js_code = f"""
        const target = document.getElementById('hud-target');
        const textScore = document.getElementById('hud-text-score');
        const visScore = document.getElementById('hud-visual-score');
        const combScore = document.getElementById('hud-combined-score');
        const status = document.getElementById('hud-status');
        const graph = document.getElementById('hud-graph');

        // Only set a default if empty; never overwrite typed value
        if (target) {{
            if (!target.value) target.value = '{target_word}';
            target.style.color = '{mode_color}';
        }}

        if (textScore) textScore.innerText = '{text_score:.3f}';
        if (visScore) visScore.innerText = '{visual_score:.3f}';

        if (combScore) {{
            combScore.innerText = '{combined_score:.3f}';
            combScore.style.color = {combined_score} > 0.3 ? '#00f2ea' : '#fff';
        }}

        if (status) status.innerText = '{status_text}';

        if (graph && '{graph_base64}') {{
            graph.src = 'data:image/png;base64,{graph_base64}';
        }}
        """
        try:
            self.driver.execute_script(js_code)
        except Exception as e:
            print(f"Failed to update HUD: {e}")

    # Optional helper (still fine to keep)
    def set_target_word(self, word: str):
        safe = word or ""
        self.driver.execute_script(
            """
            const el = document.getElementById('hud-target');
            if (el) el.value = arguments[0];
            """,
            safe,
        )
