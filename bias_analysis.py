import os
import re
import numpy as np
import fasttext
import nltk
from nltk.corpus import stopwords

class Relatedness:
    # IMPORTANT: set this to your real model path
    MODEL_PATH = r"C:\Users\kyabr\PersonalProjects\HackaCookers\models\cc.en.300.bin"

    model = None
    STOPWORDS = None

    @staticmethod
    def _ensure_loaded():
        # Load stopwords once
        if Relatedness.STOPWORDS is None:
            try:
                Relatedness.STOPWORDS = set(stopwords.words("english"))
            except LookupError:
                nltk.download("stopwords")
                Relatedness.STOPWORDS = set(stopwords.words("english"))

        # Load fastText model once
        if Relatedness.model is None:
            if not os.path.isfile(Relatedness.MODEL_PATH):
                raise FileNotFoundError(f"Model file not found:\n{Relatedness.MODEL_PATH}")

            print("Loading fastText model...", flush=True)
            Relatedness.model = fasttext.load_model(Relatedness.MODEL_PATH)
            print("Model loaded.", flush=True)

    @staticmethod
    def _clean_word(w: str) -> str:
        w = (w or "").lower().strip()
        w = re.sub(r"[^a-z]", "", w)
        if len(w) <= 2:
            return ""
        if w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        if Relatedness.STOPWORDS and w in Relatedness.STOPWORDS:
            return ""
        return w

    @staticmethod
    def most_related_words(seed_words, topn: int = 25, exclude_seed: bool = True, candidates: int = 200000):
        Relatedness._ensure_loaded()

        cleaned = [Relatedness._clean_word(w) for w in seed_words]
        cleaned = [w for w in cleaned if w]
        if not cleaned:
            return []

        # combined concept vector
        vecs = [Relatedness.model.get_word_vector(w) for w in cleaned]
        concept_vec = np.mean(np.stack(vecs), axis=0).astype(np.float32)
        concept_vec /= (np.linalg.norm(concept_vec) + 1e-12)

        # build candidate list from vocab
        words, freqs = Relatedness.model.get_words(include_freq=True)
        seed_set = set(cleaned)

        # optionally limit candidates for speed
        # (most frequent words first)
        if candidates and candidates < len(words):
            words = words[:candidates]

        # compute cosine similarity against each vocab word
        sims = []

        for w in words:
            out = []
            seen = set()
            for w, s in sims:
                if w in seen:
                    continue
                seen.add(w)
                out.append((w, s))
                if len(out) >= topn:
                    break

            return out

    @staticmethod
    def clean_word_list(words):
        """
        Normalize, remove stopwords, remove duplicates, preserve order
        """
        Relatedness._ensure_loaded()

        cleaned = []
        seen = set()

        for w in words:
            cw = Relatedness._clean_word(w)
            if not cw:
                continue
            if cw in seen:
                continue
            seen.add(cw)
            cleaned.append(cw)

        return cleaned


    @staticmethod
    def count_word_appearances(words):
        """
        Count the number of appearances for each word after cleaning.
        Returns a dictionary with cleaned words as keys and counts as values,
        sorted by frequency (most frequent first).
        """
        Relatedness._ensure_loaded()
        
        word_counts = {}
        
        for w in words:
            cw = Relatedness._clean_word(w)
            if cw:  # Only count non-empty cleaned words
                word_counts[cw] = word_counts.get(cw, 0) + 1
        
        # Sort by count (descending)
        sorted_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_counts


if __name__ == "__main__":
    print("=== Word Count Analysis ===")
    
    words = [
    "you", "know", "the", "6", "7", "guy", "oh", "its", "the", "monarch",
    "its", "the", "monarch", "yeah", "yeah", "the", "guy", "that", "made",
    "the", "song", "he", "does", "antarilla", "yeah", "yeah", "but", "he",
    "wears", "masks", "do", "you", "see", "the", "masks", "no", "i",
    "didnt", "and", "all", "of", "his", "music", "video", "he", "wears",
    "really", "creepy", "masks", "oh", "theres", "so", "much", "footage",
    "of", "him", "and", "he", "even", "said", "to", "himself", "theres",
    "pictures", "of", "him", "holding", "goat", "heads", "up", "yeah",
    "yeah", "sacrificing", "animals", "and", "hes", "saying", "his",
    "religion", "it", "uses", "animal", "sacrifice", "yeah", "theres",
    "certain", "gods", "he", "prays", "to", "that", "give", "him", "what",
    "he", "wants", "out", "of", "life", "yeah", "by", "sacrificing", "or",
    "giving", "offerings", "to", "him", "this", "is", "like", "real",
    "witchcraft", "yeah", "thats", "when", "you", "say", "six", "thats",
    "a", "goddess", "say", "seven", "thats", "also", "a", "goddess",
    "so", "what", "hes", "saying", "say", "nothing", "at", "this",
    "but", "i", "actually", "dont", "know", "where", "6", "7", "came",
    "with", "that", "such", "a", "random", "number", "though", "so",
    "the", "theory", "is", "6", "7", "is", "supposed", "to", "be",
    "something", "that", "we", "dont", "understand", "but", "it",
    "conjures", "almost", "a", "spirit", "its", "like", "chanting",
    "onto", "it", "its", "like", "a", "name", "or", "almost", "like",
    "a", "prayer", "to", "just", "say", "you", "know", "how", "we",
    "say", "like", "hallelujah", "yeah",  "but", "the", "weight", "lifting", "but", "no", "the", "girl", "gets",
    "up", "and", "you", "see", "i", "want", "to", "be", "more", "but",
    "i", "have", "somebody", "watch", "it", "i", "want", "to", "be",
    "more", "of", "you", "sir", "i", "want", "to", "really", "yeah",
    "but", "she", "gets", "it", "drop", "the", "thing", "walks", "off",
    "the", "stage", "crying", "her", "mothers", "crying", "her",
    "fathers", "crying", "guy", "gets", "up", "he", "said", "have",
    "you", "lifted", "before", "a", "little", "bit", "and", "he",
    "walks", "up", "being", "he", "could", "have", "gone", "ding",
    "ding", "ding", "i", "think", "it", "was", "112", "pounds", "and",
    "its", "crazy", "or", "the", "beautiful", "boxer", "that", "boxing",
    "you", "know", "and", "that", "they", "have", "a", "young",
    "gentleman", "who", "transitioned", "theres", "a", "very", "good",
    "boxer", "but", "he", "wanted", "to", "be", "a", "woman", "which",
    "you", "know", "to", "each", "is", "odd", "because", "i", "want",
    "to", "be", "very", "liberal", "when", "it", "comes", "to", "these",
    "subjects", "im", "trying", "to", "get", "that", "vote", "its",
    "not", "an", "easy", "vote", "to", "get", "its", "very", "tough",
    "for", "me", "to", "get", "it", "but", "he", "transitioned", "and",
    "hes", "he", "transitioned", "and", "the", "girl", "was", "a",
    "champion", "boxer", "from", "italy", "remember", "she", "got",
    "up", "first", "round", "he", "hit", "a", "boom", "with", "a",
    "left", "a", "left", "for", "those", "everybody", "in", "his",
    "butt", "but", "a", "left", "lisa", "knows", "better", "than",
    "anybody", "but", "a", "left", "is", "difference", "he", "goes",
    "boom", "shes", "like", "oh", "my", "she", "walked", "to", "the",
    "corner", "remember", "she", "didnt", "go", "down", "but", "she",
    "did", "everything", "else", "she", "said", "ive", "never", "been",
    "hit", "like", "that", "before", "i", "dont", "want", "to", "go",
    "out", "again", "you", "can", "do", "it", "you", "can", "do", "it",
    "bang", "she", "walked", "off", "she", "said", "thats", "its",
    "he", "happened", "to", "win", "the", "gold", "medal", "that",
    "young", "woman", "you", "won", "the", "gold", "medal", "there",
    "were", "two", "transition", "people", "they", "both", "won",
    "gold", "medals", "the", "whole", "thing", "is", "ridiculous",
    "you", "have", "policy", "on", "your", "side", "they", "dont",
    "have", "policy", "on", "your", "side", "but", "youre", "policy",   "and", "this", "doesnt", "have", "a", "plan", "she", "copied",
    "bidens", "plan", "and", "its", "like", "four", "sentences",
    "like", "runspot", "run", "crime", "in", "this", "country",
    "is", "through", "the", "roof", "and", "we", "have", "a",
    "new", "form", "of", "crime", "its", "called", "my", "grade",
    "crime", "and", "its", "happening", "at", "levels", "and",
    "nobody", "thought", "possible", "this", "is", "so", "rich",
    "coming", "from", "someone", "who", "has", "been",
    "prosecuted", "for", "national", "security", "crimes",
    "economic", "crimes", "election", "interference", "looks",
    "like", "a", "lie", "for", "sexual", "assault", "and", "his",
    "next", "big", "court", "appearance", "is", "in", "november",
    "of", "his", "own", "criminal", "sentencing", "the",
    "importance", "of", "american", "diplomacy", "where", "we",
    "invite", "and", "receive", "respected", "world", "leaders",
    "and", "this", "former", "president", "as", "president",
    "theyre", "eating", "the", "dogs", "the", "people", "that",
    "came", "in", "theyre", "eating", "theyre", "eating", "the",
    "pets", "there", "have", "been", "no", "credible", "reports",
    "of", "specific", "claims", "of", "pets", "being", "harmed",
    "interred", "or", "abused", "by", "individuals", "within",
    "the", "immigrant", "community", "the", "last", "thing",
    "people", "on", "television", "say", "here", "this", "is",
    "the", "thing", "the", "people", "on", "television", "say",
    "my", "dog", "was", "taken", "and", "used", "for", "food",
    "so", "maybe", "he", "said", "that", "and", "maybe", "thats",
    "a", "good", "thing", "to", "say", "for", "a", "city",
    "manager", "im", "not", "taking", "this", "from",
    "television", "but", "the", "people", "on", "television",
    "say", "my", "dog", "was", "eaten", "by", "the", "people",
    "that", "went", "there", "you", "talk", "about", "extreme",
    "i", "have", "talked", "with", "military", "leaders", "some",
    "of", "whom", "work", "with", "you", "and", "they", "say",
    "youre", "a", "disgrace", "and", "when", "you", "then",
    "talk", "in", "this", "way", "in", "a", "presidential",
    "debate", "and", "deny", "what", "over", "and", "over",
    "again", "are", "court", "cases", "you", "have", "lost",
    "because", "you", "did", "in", "fact", "lose", "that",
    "election", "it", "leads", "one", "to", "believe", "that",
    "perhaps", "we", "do", "not", "have", "in", "the",
    "candidate", "to", "my", "right", "the", "temperament",
    "or", "the", "ability", "to", "not", "be", "confused",
    "about", "fact", "thats", "deeply", "troubling", "and",
    "the", "american", "people", "deserve", "better"
    ]

    cleaned_words = Relatedness.clean_word_list(words)

    print("Original word count:", len(words))
    print("Cleaned word count:", len(cleaned_words))
    print("Cleaned words:", cleaned_words[:30], "...")

    # Count word appearances
    word_counts = Relatedness.count_word_appearances(words)
    
    print("\n=== Word Frequency Analysis ===")
    print(f"Total unique cleaned words: {len(word_counts)}")
    print("\nTop 30 most frequent words:")
    for word, count in word_counts[:30]:
        print(f"{count:3d}x  {word}")
    
    print("\n✅ Word count analysis completed successfully.")