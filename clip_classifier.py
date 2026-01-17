import torch
import clip
from PIL import Image

class ClipClassifier:
    def __init__(self, model_name="ViT-B/32", device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading CLIP model '{model_name}' on {self.device}...")
        self.model, self.preprocess = clip.load(model_name, device=self.device)

    def classify(self, image_path, labels):
        """
        Classifies an image against a list of text labels.
        img_path: Path to the image file.
        labels: List of strings (e.g., ["a cat", "a dog"]).
        Returns: Dictionary with 'top_label', 'top_score', and 'all_scores'.
        """
        try:
            image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(self.device)
            text = clip.tokenize(labels).to(self.device)

            with torch.no_grad():
                image_features = self.model.encode_image(image)
                text_features = self.model.encode_text(text)
                
                logits_per_image, logits_per_text = self.model(image, text)
                probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

            # Map scores to labels
            results = {label: float(score) for label, score in zip(labels, probs)}
            
            # Sort by score descending
            sorted_results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))

            top_label = list(sorted_results.keys())[0]
            top_score = list(sorted_results.values())[0]

            return {
                "top_label": top_label,
                "top_score": top_score,
                "all_scores": sorted_results
            }

        except Exception as e:
            print(f"Error classifying image: {e}")
            return None

if __name__ == "__main__":
    # Test
    # Create a dummy image or prompt user
    print("ClipClassifier module ready.")
