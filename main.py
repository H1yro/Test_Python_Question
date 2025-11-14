import telebot
import requests
import json
import random
import config
import os

TELEGRAM_BOT_TOKEN = config.Test_Python
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_ACCESS_TOKEN = config.access_token
GIGACHAT_MODEL = "GigaChat:latest"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

HINTS = [
    "Подумайте, какие базовые структуры данных лучше всего подходят для этой задачи.",
    "Разбейте задачу на более мелкие подзадачи. Каждую подзадачу можно решить отдельно.",
    "Попробуйте написать псевдокод, чтобы структурировать вашу мысль.",
    "Изучите документацию по стандартным библиотекам вашего языка программирования. Возможно, там есть готовые решения.",
    "Погуглите! Но не ищите готовый ответ, а ищите информацию по конкретным темам."
]

ENCOURAGEMENTS = [
    "Не плохой ход мыслей!",
    "Вы на правильном пути! Продолжайте искать решение.",
    "Не бойтесь экспериментировать!",
    "Каждая ошибка - это шаг к успеху.",
    "У вас все получится!"
]

def get_gigachat_response(prompt):
    headers = {
        "Authorization": f"Bearer {GIGACHAT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GIGACHAT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "top_p": 0.9,
        "n": 1,
        "stream": False,
        "max_tokens": 800
    }
    try:
        response = requests.post(GIGACHAT_API_URL, headers=headers, json=data, timeout=60, verify=False)
        response.raise_for_status()
        json_response = response.json()
        if "choices" in json_response and len(json_response["choices"]) > 0:
            return json_response["choices"][0]["message"]["content"]
        else:
            return "Ошибка: Не удалось получить ответ от Gigachat. Проверьте структуру ответа."
    except requests.exceptions.RequestException as e:
        return f"Ошибка при запросе к Gigachat API: {e}"
    except json.JSONDecodeError as e:
        return f"Ошибка при разборе JSON ответа от Gigachat: {e} Response text: {response.text if 'response' in locals() else 'No response'}"
    except Exception as e:
        return f"Произошла непредвиденная ошибка: {e}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Готов? Если нужно больше информации то напиши /help")

@bot.message_handler(commands=['help'])
def send_whelp(message):
    bot.reply_to(message, "Привет! Я бот-помощник по программированию.  Я не дам готовый ответ, но помогу тебе подумать над задачей.  Просто опиши свою проблему.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text
    gigachat_prompt = f"""Пользователь пытается решить задачу по программированию: "{user_message}".
                         Какую ОДНУ конкретную подсказку, наводящий вопрос или совет ты можешь ему дать,
                         чтобы он сам нашел решение?  Будь максимально полезным, но не давай готовый код.
                         Твой ответ должен быть коротким (не более 2-3 предложений)."""
    gigachat_response = get_gigachat_response(gigachat_prompt)

    random_hint = random.choice(HINTS)
    random_encouragement = random.choice(ENCOURAGEMENTS)

    response_text = f"""Вот несколько советов, которые могут тебе помочь:

1.  {gigachat_response}

2.  {random_hint}

3.  {random_encouragement}

Попробуй еще раз!  У тебя все получится!
"""
    bot.reply_to(message, response_text)

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Бот упал с ошибкой: {e}")