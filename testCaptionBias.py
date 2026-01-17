import captionBias

c = captionBias.Concept("dance")

tests = [
    "This is a dance video with great moves",
    "Cooking pasta with garlic and oil",
    "🔥🔥🔥",
    "",
]

for t in tests:
    score = c.biasScore(t)
    print(f"{t!r} -> {score} ({type(score)})")
