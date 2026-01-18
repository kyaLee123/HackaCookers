import os
import urllib.request
import gzip
import shutil
import re
import numpy as np
import fasttext
import nltk
from nltk.corpus import stopwords

# ----------------------------
# Optional: Numberbatch fetch (kept exactly as in your script)
# ----------------------------
NB_GZ = "numberbatch-en-19.08.txt.gz"
NB_TXT = "numberbatch-en-19.08.txt"
NB_URL = "https://conceptnet.s3.amazonaws.com/downloads/2019/numberbatch/numberbatch-en-19.08.txt.gz"

if not os.path.exists(NB_GZ) and not os.path.exists(NB_TXT):
    print("Downloading Numberbatch...", flush=True)
    urllib.request.urlretrieve(NB_URL, NB_GZ)
    print("Downloaded:", NB_GZ, flush=True)

if os.path.exists(NB_GZ) and not os.path.exists(NB_TXT):
    print("Extracting Numberbatch...", flush=True)
    with gzip.open(NB_GZ, "rb") as f_in, open(NB_TXT, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    print("Extracted:", NB_TXT, flush=True)


# ----------------------------
# Class mirroring the "Concept" format
# ----------------------------
class Relatedness:
    """
    Class representing a target word/idea, used to score how strongly
    a caption is related to it in the range [0, 1].
    """

    # Path to your fastText model
    MODEL_PATH = r"C:\Users\kyabr\PersonalProjects\HackaCookers\models\cc.en.300.bin"

    # fastText model + stopwords (loaded once)
    model = None
    STOPWORDS = None

    # Load shared resources once
    @staticmethod
    def _ensure_loaded():
        # Stopwords
        if Relatedness.STOPWORDS is None:
            try:
                Relatedness.STOPWORDS = set(stopwords.words("english"))
            except LookupError:
                nltk.download("stopwords")
                Relatedness.STOPWORDS = set(stopwords.words("english"))

        # fastText model
        if Relatedness.model is None:
            if not os.path.isfile(Relatedness.MODEL_PATH):
                raise FileNotFoundError(f"Model file not found:\n{Relatedness.MODEL_PATH}")

            print("Loading fastText model (this can take a while and may use lots of RAM)...", flush=True)
            Relatedness.model = fasttext.load_model(Relatedness.MODEL_PATH)
            print("Model loaded.", flush=True)

    # Store the "concept"/target word
    def __init__(self, word: str):
        Relatedness._ensure_loaded()
        self.word = word

    # --- Your helpers (same functionality) ---

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"#", " ", text)
        text = re.sub(r"[^a-z\s]", " ", text)

        tokens = text.split()
        cleaned = []

        for t in tokens:
            if len(t) <= 2:
                continue
            if t.endswith("s") and not t.endswith("ss"):
                t = t[:-1]
            if t in Relatedness.STOPWORDS:
                continue
            cleaned.append(t)

        return cleaned

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    # --- Public scoring API (mirrors biasScore-style) ---

    def score(
        self,
        caption: str,
        tau: float = 0.35,
        k: float = 12.0,
        high: float = 0.45,
        bonus: float = 0.05
    ) -> float:
        """
        Scores how related `caption` is to this instance's `word` in [0, 1].
        (Same behavior as your relatedness_score function.)
        """
        tokens = self._tokenize(caption)
        if not tokens:
            return 0.0

        q = Relatedness.model.get_word_vector(self.word)
        sims = np.array(
            [self._cosine(q, Relatedness.model.get_word_vector(tok)) for tok in tokens],
            dtype=np.float32
        )

        best = float(sims.max())
        count = int(np.sum(sims >= high))

        base = 1.0 / (1.0 + np.exp(-k * (best - tau)))
        score = base + bonus * max(0, count - 1)
        return float(min(1.0, score))


