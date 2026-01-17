from sentence_transformers import SentenceTransformer
import numpy as np

# Class representing an abstract idea, used to determine how strongly some text supports or opposes that idea
class Concept:
    # The model that we are using to determine how much text algins with our concept
    model = SentenceTransformer("intfloat/e5-small-v2")

    # Precompute the positive and negative vectors for this concept
    def __init__(self, concept):
        self.vPos, self.vNeg, self.vConcept = self._conceptVectors(concept)

    # Get example sentences supporting and opposing the concept
    def _conceptVectors(self, concept):
        pos = [
            f"This text supports {concept}.",
            f"The author is in favor of {concept}.",
            f"This text praises {concept}.",
            f"The writer has a positive view of {concept}."
            ]
        neg = [
            f"This text opposes {concept}.",
            f"The author is against {concept}.",
            f"This text criticizes {concept}.",
            f"The writer has a negative view of {concept}."
            ]
        center = [
            f"This text is about {concept}.",
            f"The topic of this text is {concept}.",
            f"This discusses {concept}."
            ]
        return self._embedAverage(pos), self._embedAverage(neg), self._embedAverage(center)

    # Embed each sentence and return their mean vector
    def _embedAverage(self, texts):
        return np.mean(Concept.model.encode(texts, normalize_embeddings=True), axis=0)

    # Scores text based on how biased it is in the range [-1, 1]
    def biasScore(self, text):
        v_t = Concept.model.encode([text], normalize_embeddings=True)[0]
        
        # Get how postive, negative, and relevant the text is
        pos = np.dot(v_t, self.vPos)
        neg = np.dot(v_t, self.vNeg)
        rel = np.dot(v_t, self.vConcept)

        # Compute the raw score
        raw = pos - neg

        # Normalize the raw score
        raw = raw / (abs(raw) + 1e-8)

        # Make sure that the relevance is clamped correctly
        rel = max(0, rel)

        return raw * rel