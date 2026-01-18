# Impartial Prejudice
A TikTok algorithm curator
## Installation
Navigate to powershell and run the following:
```bash
git clone https://github.com/kyaLee123/HackaCookers.git
cd HackaCookers
```
From there, you will be required to download a number of dependencies. The first is a model used to categorise words, which you can download here: [(6.73 GB .bin file)](https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz). The absolute path for this model must then be put as a string in captionBias.py under the variable MODEL_PATH. You must also download some libraries, which can be done by running the following on powershell:
```bash
pip install clip fasttext_wheel matplotlib nltk numpy openai_whiser paddleocr Pillow playwright selenium sentence_transformers torch transformers yt_dlp
```
## Running
Navigate to powershell and run the following:
```bash
python main.py
```
Afterwards, complete the steps presented in the terminal when prompted.
## Author
Created by Kya Broderick, Anders Currah, Angie Shin, Gavin Grubert, Tusher Khondaker. Feel free to reach out to at through our emails:
grubertgavin@gmail.com
anderscurrah@gmail.com
kyabroderick@gmail.com
jeonghee0629@gmail.com
## License
I have licensed this project under CC BY-NC-SA 4.0, find the details here:
https://creativecommons.org/licenses/by-nc-sa/4.0/