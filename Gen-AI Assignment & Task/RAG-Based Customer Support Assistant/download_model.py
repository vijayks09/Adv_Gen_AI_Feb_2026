# download_model.py
import os
from transformers import T5ForConditionalGeneration, T5Tokenizer

HF_TOKEN = "YOUR_HF_TOKEN_HERE" 


model_name = "google/flan-t5-small"
save_path = "./models/flan-t5-small"
os.makedirs(save_path, exist_ok=True)

print("Downloading tokenizer...")
tokenizer = T5Tokenizer.from_pretrained(model_name, token=HF_TOKEN)
tokenizer.save_pretrained(save_path)
print("Tokenizer saved.")

print("Downloading model weights (~300MB, please wait)...")
model = T5ForConditionalGeneration.from_pretrained(
    model_name,
    token=HF_TOKEN,
    low_cpu_mem_usage=True 
)
model.save_pretrained(save_path)
print(f"\n✅ Model saved to {save_path}")

# Verify
files = os.listdir(save_path)
print(f"Files: {files}")