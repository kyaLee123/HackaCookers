# Test example showing off the bias script
from bias import Concept

concept = Concept("puppies")

# Text biased against that concept have a negative score
print("Negative Text")
print(concept.biasScore("I really hate puppies"))
print(concept.biasScore("puppies are the worst"))
print(concept.biasScore("I want to drop kick a puppy"))

# Text biased for that concept have a positive score
print("Positive Text")
print(concept.biasScore("I really love puppies"))
print(concept.biasScore("puppies are the best"))
print(concept.biasScore("I want to adopt a cute puppy"))

# Irrelevant text has a low or 0 score
print("Irrelevant Text")
print(concept.biasScore("I really love cars"))
print(concept.biasScore("oranges are the best"))
print(concept.biasScore("I enjoyed my trip to mexico"))