import torch
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
from pydub import AudioSegment
import numpy as np
import os
import argparse
import re

def remove_page_numbers(text):
    """Remove 'Page X:' patterns from the text."""
    return re.sub(r'Page \d+:', '', text)

def format_title(filename):
    """Format the filename into a readable title."""
    title = os.path.splitext(filename)[0]  # Remove the file extension
    title = title.replace('_', ' ').replace('-', ' ')  # Replace underscores/dashes with spaces
    title = title.title()  # Capitalize the title appropriately
    return title

def remove_page_numbers(text):
    """Remove 'Page X:' patterns from the text."""
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

def process_chunk(chunk, model, processor, speaker_embeddings, vocoder):
    inputs = processor(text=chunk, return_tensors="pt")
    with torch.no_grad():
        return model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Batch Text to Speech Conversion")
parser.add_argument("folder_path", type=str, help="Path to the folder containing text files")
args = parser.parse_args()

# Load the dataset, vocoder, and models
embeddings_dataset = load_dataset("MikhailT/speaker-embeddings", 'utterance_embeddings')
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")

# Target speaker ID
target_speaker_id = '030'
speaker_embeddings = None
for record in embeddings_dataset['cmu_arctic']:
    if record['speaker_id'] == target_speaker_id:
        speaker_embeddings = torch.tensor(record['embedding']).unsqueeze(0)
        break

if speaker_embeddings is not None:
    for root, dirs, files in os.walk(args.folder_path):
        for file_name in files:
            if file_name.endswith('.txt') and file_name != 'cover.txt':
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()

                # Format and add the title to the beginning of the text
                title = format_title(file_name)
                formatted_text = f"The title of this book is {title}. {text}"

                # Clean the text by removing page numbers
                cleaned_text = remove_page_numbers(formatted_text)

                text_chunks = split_text(cleaned_text, max_length=600)
                full_audio = []
                for chunk in text_chunks:
                    audio_output = process_chunk(chunk, model, processor, speaker_embeddings, vocoder)
                    full_audio.append(audio_output.numpy().squeeze())

                full_audio = np.concatenate(full_audio)
                full_audio = full_audio / np.max(np.abs(full_audio))
                full_audio = np.int16(full_audio * 32767)

                output_file_path = os.path.join(root, os.path.splitext(file_name)[0] + ".mp3")

                audio_segment = AudioSegment(full_audio.tobytes(), frame_rate=16000, sample_width=2, channels=1)
                audio_segment.export(output_file_path, format="mp3")
                print(f"Generated speech saved as {output_file_path}.")
else:
    print(f"Speaker with ID {target_speaker_id} not found.")