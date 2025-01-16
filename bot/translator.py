from translate import Translator

user_languages = {}

def set_user_language(user_id: int, selected_language: str):
    user_languages[user_id] = selected_language

def get_user_language(user_id: int) -> str:
    return user_languages.get(user_id, "en")

def translate_message(message: str, user_id: int) -> str:
    language = get_user_language(user_id)
    if language == "en":
        return message
    elif language == "ru":
        translator = Translator(to_lang="ru")
        return translator.translate(message)
