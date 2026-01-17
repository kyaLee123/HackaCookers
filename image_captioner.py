from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image

class ImageCaptioner:
    def __init__(self, model_name="nlpconnect/vit-gpt2-image-captioning", device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading Image Captioning model '{model_name}' on {self.device}...")
        
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.feature_extractor = ViTImageProcessor.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        self.model.to(self.device)

    def generate_caption(self, image_path, max_length=16, num_beams=4):
        """
        Generates a caption for the image at image_path.
        """
        try:
            image = Image.open(image_path)
            if image.mode != "RGB":
                image = image.convert("RGB")

            pixel_values = self.feature_extractor(images=[image], return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)

            output_ids = self.model.generate(
                pixel_values,
                max_length=max_length,
                num_beams=num_beams
            )

            preds = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
            caption = preds[0].strip()
            return caption

        except Exception as e:
            print(f"Error generating caption: {e}")
            return ""

if __name__ == "__main__":
    # Test
    print("ImageCaptioner module ready.")
