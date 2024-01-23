import os
import torch
from transformers import pipeline
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play
import argparse

# Function for TTS
def run_tts(text, output_path, cache_dir=None, speaker="Ana Florence"):
    if cache_dir:
        os.environ['TRANSFORMERS_CACHE'] = cache_dir
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
def main(text, output_file_name, play_audio_flag, cache_location=None):
    if cache_location:
        os.environ['TRANSFORMERS_CACHE'] = cache_location

    # Run TTS
    wav_path = run_tts(text, output_file_name)

    # Play the audio if the flag is set
    if play_audio_flag:
        play_audio(wav_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run TTS and optionally play audio.')
    parser.add_argument('--text', type=str, required=True, help='Text to convert to speech.')
    parser.add_argument('--output', type=str, default='generated_speech.mp3', help='Output file name.')
    parser.add_argument('--play', action='store_true', help='Flag to play audio after generation.')
    parser.add_argument('--cache', type=str, help='Optional cache location for transformer models.')

    args = parser.parse_args()
    main(args.text, args.output, args.play, args.cache)
