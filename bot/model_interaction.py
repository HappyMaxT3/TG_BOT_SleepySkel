from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
from bot.storage import get_user_name
import torch
import random

def load_model_with_progress(model_name="bigscience/bloomz-1b7"):
    progress_bar = tqdm(total=2, desc="loading")

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

def load_sleep_advice(file_path="bot/sleep_advice.txt") -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            advice_list = file.readlines()
        return [advice.strip() for advice in advice_list if advice.strip()]
    except FileNotFoundError:
        return ["I'm sorry, but I don't have sleep advice at the moment."]

def generate_sleep_response(user_input: str, advice_list: list) -> str:
    relevant_advice = random.choice(advice_list)
    response = (
        f"Dreams and nightmares can be influenced by your daily life. Here's something to consider: {relevant_advice}. "
        f"Try to relax before bedtime to improve your sleep."
    )
    return response

def get_model_response(model, tokenizer, user_input: str, user_id) -> str:
    name = get_user_name(user_id)
    sleep_advice = load_sleep_advice()

    if any(word in user_input.lower() for word in [
    "dream", "nightmare", "sleep", "tired", "insomnia", "fatigue", "rest", "wake", "energy", 
    "relax", "caffeine", "melatonin", "circadian", "drowsy", "fatigued", "recharge", "sleepy", 
    "snooze", "nap", "restful", "deep sleep", "sleep cycle", "sleep deprivation", "bedtime", 
    "sleeping", "brain waves", "overstimulated", "overwork", "sleep hygiene", "REM sleep", 
    "sleeping patterns", "chronic fatigue", "good sleep", "quality sleep", "relaxation", 
    "dreams", "restorative sleep", "sleep disorders", "body clock", "sleep environment", 
    "unwinding", "sleep therapy"
    ]):

        advice_response = generate_sleep_response(user_input, sleep_advice)
        prompt = f"{name}: {user_input}\n\n💀💤: {advice_response}\nAnswer: "

        inputs = tokenizer.encode(prompt, return_tensors="pt")
        outputs = model.generate(inputs, max_new_tokens=250)

        final_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return f"{name}: {user_input}\n\n💀💤: " + final_response.split("Answer:")[-1].strip()
    
    else:
        prompt = f"{name}: {user_input}\n\n💀💤: "

        inputs = tokenizer.encode(prompt, return_tensors="pt")
        outputs = model.generate(inputs, max_new_tokens=160)

        final_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return final_response.split("Answer:")[-1].strip()
