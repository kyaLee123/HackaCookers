import biasFunctions.captionBias as captionBias
import biasFunctions.imageClassificationBias as imageBias

c = imageBias.Concept("animal")


tests  = [
        "a man and woman in the park",
        "a man standing in front of his computer",
        "a woman looking at a picture of a dog",
        "a boy playing the guitar"
    ]

for t in tests:
    score = c.biasScore(t)
    print(f"{t!r} -> {score} ({type(score)})")
