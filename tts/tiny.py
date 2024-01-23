import os
os.environ['TRANSFORMERS_CACHE'] = 'E:/model'
import os
import torch
from transformers import pipeline
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play

# Function for TTS
def run_tts(text, output_path, speaker="Ana Florence"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    temp_wav_path = "temp_output.wav"
    tts.tts_to_file(text=text, speaker=speaker, language="en", file_path=temp_wav_path)
    wav_audio = AudioSegment.from_wav(temp_wav_path)
    wav_audio.export(output_path, format="mp3")
    return temp_wav_path

# Function to play audio
def play_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    play(audio)

# Main function
def main():

    text = ""
    # Run TTS
    output_path = "generated_speech.mp3"  # Set your desired output file name
    wav_path = run_tts(text, output_path, speaker="Ana Florence")

    # Play the audio
    play_audio(wav_path)

if __name__ == "__main__":
    main()
