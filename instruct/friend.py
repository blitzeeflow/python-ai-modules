import os
os.environ['TRANSFORMERS_CACHE'] = 'E:\model'
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
device = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_default_device("cuda")

def split_and_get_first(text):
    parts = text.split('<|endoftext|>')
    return parts[0] if len(parts) > 0 else ''  # Return empty string if no '<|endoftext|>' is found in the input text.

model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype="auto", trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)

prompt = """You are a digital companion named Emily, designed to engage and interact with children through voice-based activities. Your primary functions include roleplaying various characters and scenarios based on the child's imagination and playing voice-activated games such as "Rock, Paper, Scissors" and various word games. You are equipped to understand and respond to a child's voice, encouraging creativity, storytelling, and language skills. Remember to adapt your responses to be age-appropriate, engaging, and educational, fostering a safe and fun learning environment. When roleplaying, use vivid descriptions and interactive storytelling to bring the scenarios to life. For games, provide clear instructions and positive feedback to make the experience enjoyable and rewarding for the child."""
output_termination = "\nOutput:"
total_input = f"Instruct:{prompt}{output_termination}"
inputs = tokenizer(total_input, return_tensors="pt", return_attention_mask=True)
inputs = inputs.to(device)
eos_token_id = tokenizer.eos_token_id
max_length = 1000
outputs = model.generate(**inputs, max_length=max_length, eos_token_id=eos_token_id)

# Find the position of "Output:" and extract the text after it
generated_text = tokenizer.batch_decode(outputs)[0]

# Split the text at "Output:" and take the second part
split_text = generated_text.split("Output:", 1)
assistant_response = split_text[1].strip() if len(split_text) > 1 else ""
assistant_response = assistant_response.replace("<|endoftext|>", "").strip()
print(assistant_response)