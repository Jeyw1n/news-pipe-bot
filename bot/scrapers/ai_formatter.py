import requests


URL = "http://localhost:1234/v1/chat/completions"
system_prompt = """
Ты — помощник, который генерирует аккуратные и лаконичные посты для Телеграм-канала на основе входного текста.

Твоя задача:
— Сформировать короткий, понятный пост, который читается легко и красиво выглядит в Telegram.
— Не просто сожми текст, а пойми суть и передай ее своими словами.
— <b>Жирным выделяй только заголовок и максимум 1-2 ключевых слова в каждом абзаце.</b> Не злоупотребляй форматированием.
— Каждый пост должен начинаться с понятного, простого и интересного заголовка (до 10 слов), выделенного с помощью <b>тега</b>.
— Убери все ссылки и т.п.
— Далее — 1–3 абзаца текста. Каждый абзац — 1 краткое предложение. Без лишней "воды".
— Не используй фразы вроде: "Привет", "Итоги", "Таким образом", "Выводы", "Можно сказать", "Стоит отметить".
— Иногда используй эмодзи (если уместно).

Пиши строго по делу. Пост должен быть читаем, логичен, с понятным началом и завершением..
"""






def ask_model(text: str) -> str:
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemma-3-4b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    response = requests.post(URL, json=payload, headers=headers)
    response.raise_for_status()  # Поднимет исключение при ошибке

    answer = response.json()["choices"][0]["message"]["content"]

    # Разделяем текст и prompt для Stable Diffusion
    content_text = answer.strip()

    return content_text