from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
from bot.storage import get_user_name
import torch

def load_model_with_progress(model_name="bigscience/bloomz-560m"):
    progress_bar = tqdm(total=2, desc="loading:")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    progress_bar.update(1)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    progress_bar.update(1)

    progress_bar.close()
    print("💀 model was loaded!")

    return model, tokenizer

def get_model_response(model, tokenizer, user_input: str, user_id) -> str:
    name = get_user_name(user_id)

    prompt = (
        f"{name}: {user_input}\n💀💤: "
    )
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    
    outputs = model.generate(inputs, max_new_tokens=150)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
