from diffusers import StableDiffusionPipeline
import torch

model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id)
# Check if CUDA is available and use it, otherwise use CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)

prompt = "2D cartoon illustration of a friendly dragon working as a firefighter, extinguishing fires in a comical, fantasy-themed cityscape"
image = pipe(prompt).images[0]  
    
image.save("image.png")