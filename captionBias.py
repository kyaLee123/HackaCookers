import os
import re
import numpy as np
import fasttext


import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords

# Class mirroring the "Concept" format
class Relatedness:
    """
    Class representing a target word/idea, used to score how strongly
    a given text is related to it in the range [0, 1].
    """

    #model path
    MODEL_PATH = r'/Users/anderscurrah/Desktop/Random Coding Stuffs/Hackathons/HackaCookers/models/cc.en.300.bin'
    model = None
    STOPWORDS = None

    
    @staticmethod #load resouces once so that we don't have to grab them again
    def _ensure_loaded(): #checks loading worked
        if Relatedness.STOPWORDS is None: 
            try:
                Relatedness.STOPWORDS = set(stopwords.words("english")) #set stopwords
            except LookupError:
                nltk.download("stopwords")
                Relatedness.STOPWORDS = set(stopwords.words("english")) #trying to deal with errors

        if Relatedness.model is None:
            if not os.path.isfile(Relatedness.MODEL_PATH): #if the model path doesnt exist give an error
                raise FileNotFoundError(f"Model file not found:\n{Relatedness.MODEL_PATH}") 

            print("Loading fastText model...", flush=True) 
            Relatedness.model = fasttext.load_model(Relatedness.MODEL_PATH) #load model (this takes a while)
            print("Model loaded.", flush=True)

    def __init__(self, word: str):
        Relatedness._ensure_loaded() #make sure things are loaded before we go ahead
        self.word = word #get the work on

#tokenize the words so we can work with them more clearly (AKA split it and clean it)
    def _tokenize(self, text: str) -> list[str]:
        if not text: #if nothing then we just return nothing
            return []
        text = text.lower() #lowercase everything
        text = re.sub(r"#", " ", text) #get rid of the hashtag
        text = re.sub(r"[^a-z\s]", " ", text) #get rid of everything that isnt letter or space

        tokens = text.split() #split into tokens
        cleaned = [] #start a list to put the tokens into

        for t in tokens: #go through each token
            if len(t) <= 2: #skip short tokens
                continue
            if t.endswith("s") and not t.endswith("ss"): #if text ends in ss we keep it, but if it ends in s we remove
                t = t[:-1]
            if t in Relatedness.STOPWORDS: #if its in stopwords, we dont append it
                continue
            cleaned.append(t)

        return cleaned

    def _cosine(self, a: np.ndarray, # this is the vector rep of the keyword
                 b: np.ndarray #this is the vector rep of the token
                 ) -> float: #out output is a float of the cosine similarity
        denom = np.linalg.norm(a) * np.linalg.norm(b) #euclidian norm a  * euclidian norm b for the denominator
        if denom == 0: #just incase we get a zero value for denimonator
            return 0.0
        return float(np.dot(a, b) / denom) #this is the cosine similarity formula

    #function that outputs a bias score between a set of text and the keyword
    def score(
        self,
        caption: str, #the actual caption
        tau: float = 0.35, #the threshold for the best similarity
        k: float = 12.0, #steepness of the sigmoid
        high: float = 0.45, #the threshold for counting multiple similar words
        bonus: float = 0.05 #the bonus for each additional similar word
    ) -> float:
        """
        Scores how related `caption` is to this instance's `word` in [0, 1].
        (Same behavior as your relatedness_score function.)
        """
        tokens = self._tokenize(caption) #tokenize the caption
        if not tokens:
            return 0.0

        q = Relatedness.model.get_word_vector(self.word) #get the vector for the keyword
        sims = np.array( 
            [self._cosine(q, Relatedness.model.get_word_vector(tok)) for tok in tokens], #get cosine similarity for each token
            dtype=np.float32 
        )

        best = float(sims.max()) #get the best similarity
         #count how many tokens are above the high threshold
        count = int(np.sum(sims >= high))

        base = 1.0 / (1.0 + np.exp(-k * (best - tau))) #sigmoid function for the best similarity
        score = base + bonus * max(0, count - 1) #final score is either 0 or the base + our bonus multipled by the number of similar
        return float(min(1.0, score)) #clamp to 1.0

    # Concept-compatible call surface (NO algorithm change)
    def biasScore(self, text: str, **kwargs) -> float:
        """
        Returns float in [0,1].
        """
        return self.score(text, **kwargs)

# ----------------------------
# Drop-in alias: lets you do `c = Concept("dance")` exactly like before
# ----------------------------
Concept = Relatedness
