import openai
from bot.config import LLM_TOKEN

openai.api_key = LLM_TOKEN

async def get_model_response(user_input: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are SleepySkel, a helpful assistant who helps track and analyze sleep patterns. Your role is to provide tips, advice, and feedback on sleep-related topics."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100,
            temperature=0.7
        )
        answer = response['choices'][0]['message']['content'].strip()
        return f"💀💤 {answer}" 
    except Exception as e:
        return f"💀 Error occurred (limit reached or smth)! Please, try later.\n(If you are a developer, check the console, clumsy!)"
