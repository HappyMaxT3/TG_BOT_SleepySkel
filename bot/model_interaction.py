from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import torch

def load_model_with_progress(model_name="bigscience/bloomz-560m"):
    print("💀 Loading model...")
    progress_bar = tqdm(total=2, desc="Download progress")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    progress_bar.update(1)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    progress_bar.update(1)

    progress_bar.close()
    print("💀 Model loaded successfully!")

    return model, tokenizer

# Генерация ответа
def get_model_response(model, tokenizer, user_input: str) -> str:
    inputs = tokenizer.encode(f"User: {user_input}\nSleepySkel: ", return_tensors="pt")
    outputs = model.generate(inputs, max_new_tokens=150)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
