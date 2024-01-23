import os
import argparse
import re
import torch
from TTS.api import TTS
from pydub import AudioSegment
import numpy as np

def format_title(filename):
    title = os.path.splitext(filename)[0]
    title = title.replace('_', ' ').replace('-', ' ')
    title = title.title()
    return title

def remove_page_numbers(text):
    return re.sub(r'Page \d+:', '', text)

def split_text(text, max_length=1000):
    sentences = re.split(r'(?<=\.)\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# Parse command line arguments
parser = argparse.ArgumentParser(description="Batch Text to Speech Conversion")
parser.add_argument("folder_path", type=str, help="Path to the folder containing text files")
args = parser.parse_args()

# Initialize the new TTS model
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

for root, dirs, files in os.walk(args.folder_path):
    for file_name in files:
        if file_name.endswith('.txt') and file_name != 'cover.txt':
            file_path = os.path.join(root, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            title = format_title(file_name)
            cleaned_text = remove_page_numbers(text)
            formatted_text = f"The title of this book is {title}. {cleaned_text}"
            text_chunks = split_text(formatted_text, max_length=600)
            combined_audio = AudioSegment.silent(duration=0)
            temp_wav_path = "temp_output.wav"
            output_file_path = os.path.join(root, os.path.splitext(file_name)[0] + ".mp3")
            tts.tts_to_file(text=formatted_text,speaker="Ana Florence", language="en", file_path=temp_wav_path)
            wav_audio = AudioSegment.from_wav(temp_wav_path)
            wav_audio.export(output_file_path, format="mp3")
            print(f"Generated speech saved as {output_file_path}.")