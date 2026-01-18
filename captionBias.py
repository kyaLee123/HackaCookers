import os
import urllib.request
import gzip
import shutil
import re
import numpy as np
import fasttext
import ssl

# Safe import for secure contexts (like MacOS)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords

# ----------------------------
# Class mirroring the "Concept" format
# ----------------------------
class Relatedness:
    """
    Class representing a target word/idea, used to score how strongly
    a caption is related to it in the range [0, 1].

    Concept-compatible usage:
        from captionBias import Concept
        c = Concept("dance")
        score = c.biasScore("some caption")  # float in [0,1]
    """

    # Path to your fastText model
    # MODEL_PATH = r'/Users/anderscurrah/Desktop/Random Coding Stuffs/Hackathons/HackaCookers/models/cc.en.300.bin'
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cc.en.300.bin')
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
        if not text:
            return []
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

    # ----------------------------
    # Concept-compatible call surface (NO algorithm change)
    # ----------------------------
    def biasScore(self, text: str, **kwargs) -> float:
        """
        Alias for .score() so you can call it like your old Concept class.
        Returns float in [0,1].
        """
        return self.score(text, **kwargs)

    def __call__(self, text: str, **kwargs) -> float:
        """
        Optional: allow instance(text) as shorthand for score(text).
        """
        return self.score(text, **kwargs)


# ----------------------------
# Drop-in alias: lets you do `c = Concept("dance")` exactly like before
# ----------------------------
Concept = Relatedness
