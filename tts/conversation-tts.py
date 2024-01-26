import os
import torch
import argparse
from pydub import AudioSegment
from TTS.api import TTS
# https://github.com/KoljaB/RealtimeTTS/tree/master/tests/coqui_voices
# ['Claribel Dervla', 'Daisy Studious', 'Gracie Wise', 'Tammie Ema', 'Alison Dietlinde', 'Ana Florence', 'Annmarie Nele', 'Asya Anara', 'Brenda Stern', 'Gitta Nikolina', 'Henriette Usha', 'Sofia Hellen', 'Tammy Grit', 'Tanja Adelina', 'Vjollca Johnnie', 'Andrew Chipper', 'Badr Odhiambo', 'Dionisio Schuyler', 'Royston Min', 'Viktor Eka', 'Abrahan Mack', 'Adde Michal', 'Baldur Sanjin', 'Craig Gutsy', 'Damien Black', 'Gilberto Mathias', 'Ilkin Urbano', 'Kazuhiko Atallah', 'Ludvig Milivoj', 'Suad Qasim', 'Torcull Diarmuid', 'Viktor Menelaos', 'Zacharie Aimilios', 'Nova Hogarth', 'Maja Ruoho', 'Uta Obando', 'Lidiya Szekeres', 'Chandra MacFarland', 'Szofi Granger', 'Camilla Holmström', 'Lilya Stainthorpe', 'Zofija Kendrick', 'Narelle Moon', 'Barbora MacLean', 'Alexandra Hisakawa', 'Alma María', 'Rosemary Okafor', 'Ige Behringer', 'Filip Traverse', 'Damjan Chapman', 'Wulf Carlevaro', 'Aaron Dreschner', 'Kumar Dahl', 'Eugenio Mataracı', 'Ferran Simen', 'Xavier Hayasaka', 'Luis Moray', 'Marcos Rudaski']

# Function to trim silence from the audio
def trim_silence(audio_segment, silence_thresh=-50):
    return audio_segment.strip_silence(silence_threshold=silence_thresh)

# Function to combine audio files
def combine_audio(files, output_path):
    combined = AudioSegment.empty()
    for file in files:
        audio = AudioSegment.from_wav(file)
        combined += audio
    combined.export(output_path, format="mp3")


# Function for TTS with an index for each file
def run_tts(text, speaker, index, cache_dir=None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    temp_wav_path = f"temp_{speaker.replace(' ', '_')}_{index}.wav"
    tts.tts_to_file(text=text, speaker=speaker, language="en", file_path=temp_wav_path)
    wav_audio = AudioSegment.from_wav(temp_wav_path)
    # trimmed_audio = trim_silence(wav_audio)
    wav_audio.export(temp_wav_path, format="wav")
    return temp_wav_path

# Main function to process the transcript and generate audio
def process_transcript(transcript_file, output_file_name, cache_location=None):
    if cache_location:
        os.environ['TRANSFORMERS_CACHE'] = cache_location

    with open(transcript_file, 'r') as file:
        lines = file.readlines()

    audio_files = []
    for index, line in enumerate(lines):
        if ':' in line:
            speaker, text = line.split(':', 1)
            speaker = speaker.strip()
            text = text.strip()

            # Skip lines where text is empty
            if not text:
                print(f"Skipping line with empty text for speaker {speaker}")
                continue

            try:
                audio_file = run_tts(text, speaker, index, cache_location)
                audio_files.append(audio_file)
            except ValueError as e:
                print(f"Error processing line for speaker {speaker}: {e}")

    combine_audio(audio_files, output_file_name)

    # Clean up temporary files
    for file in audio_files:
        try:
            os.remove(file)
        except FileNotFoundError:
            print(f"Warning: Could not find the file {file} to delete.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a transcript and generate TTS audio.')
    parser.add_argument('--transcript', type=str, required=True, help='Transcript file with speaker names.')
    parser.add_argument('--output', type=str, default='combined_speech.mp3', help='Output MP3 file name.')
    parser.add_argument('--cache', type=str, help='Optional cache location for transformer models.')

    args = parser.parse_args()
    process_transcript(args.transcript, args.output, args.cache)
