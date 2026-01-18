from PIL import Image
import numpy as np

from paddleocr import PaddleOCR


class PaddleTextOCR:
    def __init__(self, output_file="imageText.txt"):
        self.output_file = output_file
        print("Loading PaddleOCR (CPU)...")
        # use_angle_cls helps sometimes with rotated text, but can slow down
        self.ocr = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)

    def classify(self, image_path):
        try:
            img = Image.open(image_path).convert("RGB")
            np_img = np.array(img)

            result = self.ocr.ocr(np_img, cls=False)

            # result format: [ [ [box], (text, conf) ], ... ]
            parts = []
            for line in result[0] if result else []:
                parts.append(line[1][0])

            text = " ".join(parts).strip()

            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(text + "\n")

            return text

        except Exception as e:
            print(f"Error extracting text with PaddleTextOCR: {e}")
            return None


if __name__ == "__main__":
    print("PaddleTextOCR module ready.")

    test_image = r"C:\Users\kyabr\PersonalProjects\HackaCookers\data\image3.png"
    ocr = PaddleTextOCR(output_file="imageText.txt")
    text = ocr.classify(test_image)
    print(text)
