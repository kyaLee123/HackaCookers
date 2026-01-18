import yt_dlp
import re
import warnings
import whisper
import os
import subprocess

# Cancel the warnings
warnings.filterwarnings("ignore", category=UserWarning)

# This class handles web scraping 
class Scraper:
    def __init__(self):
        self._resetVariables()
    
    # This function resets the variables
    def _resetVariables(self):
        self.title = None
        self.description = None
        self.channel = None
        self.transcript = None

    # Gets the info of a given TikTok video
    # includeTranscript: whether or not to include the video transcript when scraping the video (doing so significantly increases the amount of time to get the data)
    def getInfo(self, url, includeTranscript=True):
        self._resetVariables()

        ydlOpts = {
            "skip_download": True,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydlOpts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Save the information pulled from the metadata
        self.title = info.get("title") or info.get("description")
        self.description = info.get("description")
        self.channel = info.get("uploader")

        if includeTranscript:
            self.getTranscript(url)

        return self.title, self.description, self.channel, self.transcript
    
    # Gets a given TikTok video's transcript
    def getTranscript(self, url, seconds=20):
        base = "tiktok_audio"

        ydlOpts = {
            "format": "bestaudio/best",
            "outtmpl": base,
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }],
        }

        with yt_dlp.YoutubeDL(ydlOpts) as ydl:
            ydl.download([url])

        full_audio = base + ".mp3"
        short_audio = base + "_short.mp3"

        self._trimAudio(full_audio, short_audio, seconds)

        model = whisper.load_model("base")
        result = model.transcribe(short_audio)

        os.remove(full_audio)
        os.remove(short_audio)

        self.transcript = result["text"]
        return result["text"]
    
    def _trimAudio(self, inp, out, seconds):
        subprocess.run([
            "ffmpeg", "-y",
            "-i", inp,
            "-t", str(seconds),
            out
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # This function prints the data associated with the given TikTok video
    def print(self):
        def safe_print(label, value):
            try:
                print(f"{label}: {value}")
            except UnicodeEncodeError:
                print(f"{label}: {value.encode('ascii', 'replace').decode('ascii')}")

        safe_print("Title", self.title)
        safe_print("Description", self.description)
        safe_print("Channel", self.channel)
        safe_print("Transcript", self.transcript)