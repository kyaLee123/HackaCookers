from PIL import Image
import numpy as np
import easyocr


class EmojiOCR:
    def __init__(self, gpu=False, output_file="imageText.txt"):
        self.output_file = output_file
        print(f"Loading EasyOCR reader (gpu={gpu})...")
        self.reader = easyocr.Reader(['en'], gpu=gpu)

    def classify(self, image_path):
        try:
            img = Image.open(image_path)  # open image
            width, height = img.size      # get size

            bottom = int(height * 4 / 5)  # compute bottom section we want to remove
            cropped = img.crop((0, 0, width, bottom))  # remove bottom

            cropped.save("debug_easyocr_crop.png")  # save it so i can view
            np_img = np.array(cropped)              # convert to np array
            results = self.reader.readtext(np_img, detail=0)  # read results

            text = " ".join(results).strip()

            #save text
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(text + "\n")
            return text
        
        except Exception as e:
            print(f"Error extracting text with EmojiOCR: {e}")
            return None


if __name__ == "__main__":
    print("EmojiOCR module ready.")

    test_image = r"C:\Users\kyabr\PersonalProjects\HackaCookers\data\image.png"
    ocr = EmojiOCR(gpu=False)
    text = ocr.classify(test_image)
    print(text)

