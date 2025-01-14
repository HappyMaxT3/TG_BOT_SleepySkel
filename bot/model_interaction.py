from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from tqdm import tqdm
from bot.storage import get_user_name
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import SequentialChain, TransformChain
import torch
import random

def load_model_with_progress(model_name="bigscience/bloomz-1b1"):
    try:
        with tqdm(total=2, desc="Loading Model") as progress_bar:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            progress_bar.update(1)

            model = AutoModelForCausalLM.from_pretrained(model_name).to("mps")
            progress_bar.update(1)

        print("💀 Model loaded successfully!")
        return model, tokenizer
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

def create_huggingface_pipeline(model, tokenizer):
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

def load_sleep_advice(file_path="bot/sleep_advice.txt") -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [advice.strip() for advice in file if advice.strip()]
    except FileNotFoundError:
        return ["I'm sorry, but I don't have sleep advice at the moment."]
    except Exception as e:
        print(f"Error loading sleep advice: {e}")
        return []

def rephrase_advice(pipeline, advice: str, variations=3) -> list:
    responses = pipeline(
        f"Generate {variations} different ways to rephrase the following sleep advice: {advice}",
        max_length=150,
        num_return_sequences=variations,
        num_beams=variations 
    )
    return [response["generated_text"].split(": ")[-1].strip() for response in responses]

def generate_unique_response(user_input: str, advice_list: list, pipeline) -> str:
    random_advice = random.choice(advice_list)
    rephrased_variations = rephrase_advice(pipeline, random_advice)
    return random.choice(rephrased_variations)

def generate_sleep_response(user_input: str, advice_list: list, pipeline) -> str:
    return generate_unique_response(user_input, advice_list, pipeline)

def get_model_response(model, tokenizer, user_input: str, user_id) -> str:
    name = get_user_name(user_id)
    sleep_advice = load_sleep_advice()
    pipeline = create_huggingface_pipeline(model, tokenizer)
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

    prompt_template = PromptTemplate(
        input_variables=["name", "user_input", "advice_response"],
        template="{name}: {user_input}\n\n💀💤: {advice_response}\nAnswer: "
    )

    transform_chain = TransformChain(
        input_variables=["name", "user_input", "advice_response"],
        output_variables=["final_response"],
        transform=lambda inputs: {"final_response": pipeline(
            f"{inputs['name']}: {inputs['user_input']} {inputs['advice_response']}"
        )[0]["generated_text"]}
    )

    chain = SequentialChain(
        chains=[transform_chain],
        input_variables=["name", "user_input", "advice_response"],
        output_variables=["final_response"]
    )

    sleep_keywords = {
        "dream", "nightmare", "sleep", "tired", "insomnia", "fatigue", "rest", "wake", "energy",
        "relax", "caffeine", "melatonin", "circadian", "drowsy", "fatigued", "recharge", "sleepy",
        "snooze", "nap", "restful", "deep sleep", "sleep cycle", "sleep deprivation", "bedtime",
        "sleeping", "brain waves", "overstimulated", "overwork", "sleep hygiene", "REM sleep",
        "sleeping patterns", "chronic fatigue", "good sleep", "quality sleep", "relaxation",
        "dreams", "restorative sleep", "sleep disorders", "body clock", "sleep environment",
        "unwinding", "sleep therapy"
    }

    if any(keyword in user_input.lower() for keyword in sleep_keywords):
        advice_response = generate_sleep_response(user_input, sleep_advice, pipeline)
        chain_response = chain.invoke({
            "name": name,
            "user_input": user_input,
            "advice_response": advice_response
        })
        if "final_response" in chain_response:
            return chain_response['final_response'].strip()
        else:
            return "Something went wrong with the response generation."
    else:
        prompt = f"{name}: {user_input}\n\n💀💤: "
        inputs = tokenizer.encode(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        outputs = model.generate(inputs, max_new_tokens=300)
        final_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return final_response.split('💀💤:')[-1].strip()
