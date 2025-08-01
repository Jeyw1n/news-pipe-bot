import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger
import os


URL = "https://habr.com"
FILTERS = {
    "информационная безопасность",
    "информационная безопасность*"
}
headers = {"User-Agent": UserAgent().chrome}
links_history_path = os.path.join(os.path.dirname(__file__), "habr_com_history.txt")


def ask_model(text: str) -> str:
    url = "http://localhost:1234/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    system_prompt = """
        Ты — редактор Telegram-канала.

        Твоя задача:
        Преобразуй HTML-новость в связный, короткий и ясный пост для Telegram. Пиши цельным текстом, без маркированных списков. Не упрощай чрезмерно — текст должен быть понятным, но не примитивным. Передай контекст и суть лаконично, в духе качественных новостных медиа.

        Придумай краткий, цепляющий заголовок.

        Оформи пост в Markdown.

        Удали всё лишнее: даты, авторов, ссылки, технические детали, приписки и метки.

        Текст и заголовок на Русском языке!

        В конце текста добавь кодовое слово **rO4e12H@78si*$**, после которого должен следовать простой запрос на английском для Stable Diffusion — чтобы он создал тематическое изображение к посту. Не подписывай и не помечай этот запрос — просто текст. Изображение должно обязательно соответствовать теме поста.

        Описание для Stable Diffusion:
        — Пиши на английском;
        — Избегай крупных объектов, близких ракурсов и однообразия;
        — Стиль изображения должен быть в духе **хакерства**;
        — Визуал обязательно должен быть связан с содержанием текста.

        Важно:
        — Не используй структуры вроде «ключевые моменты», «итоги», «факты»;
        — Не оформляй текст списками;
        — Не дублируй очевидное (например, что закон подписал Путин, если это не добавляет смысла);
        — Один абзац — одна мысль. Весь пост должен состоять из 2–4 абзацев максимум.

        На выходе — только готовый пост для Telegram.
    """
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

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Поднимет исключение при ошибке
    return response.json()["choices"][0]["message"]["content"]    


def get_links_history() -> list[str]:
    ''' Возвращает списком историю полученных ссылок '''
    with open(links_history_path, 'r') as file:
        history = [line.strip() for line in file]
        logger.info(f"Загружено {len(history)} ссылок из истории")
        return history


def habr_com_scraper() -> list[str] | None:
    logger.info("Начинаю парсинг Habr...")

    try:
        response = requests.get(URL + "/ru/news/", headers)
    except requests.RequestException as e:
        logger.error(f"Ошибка доступа к сайту {URL}: {e}")
        return None
    
    # Извлекаем данные
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.find("div", class_="tm-articles-list").find_all("article")

    logger.info(f"Найдено {len(articles)} статей для обработки")

    filtered_links: list = []  # Список отфильтрованных по списку "FILTERS" ссылок
    links_history: list = get_links_history()  # Список прошлых ссылок, чтобы избежать повторения
    # Извлекаем ссылки и проверяем по фильтрам
    for article in articles:
        try:
            # Достаем ссылку на пост
            link = URL + article.find("a", class_="tm-title__link")["href"]
            # Сверяем его с историей ссылок и продолжаем перебор, в случае повторяющейся ссылки
            if link in links_history:
                logger.debug(f"Ссылка уже есть в истории, пропускаю: {link}")
                continue
            
            logger.debug(f"Проверяю новую ссылку: {link}")

            # Запрашиваем содержимое поста и достаем теги
            response = requests.get(link, headers)
            soup = BeautifulSoup(response.text, 'lxml')
            tags = [tag.text.lower() for tag in soup.find("div", class_="tm-publication-hubs").find_all("span")]

            # Если содержатся нужные нам теги, продолжаем
            if set(tags) & FILTERS:
                logger.info(f"Подходящая статья найдена: {link}")
                filtered_links.append(link)
            else:
                logger.debug(f"Теги не подходят, пропускаю: {link}")
                continue

        except (requests.RequestException, AttributeError) as ex:
            logger.error(f"Ошибка при обработке статьи: {ex}")

    logger.info(f"Всего подходящих новых статей: {len(filtered_links)}")
    return filtered_links


def generate_telegram_post(url):
    # Сначала получим текст со страницы
    response = requests.get(url, headers)
    soup = BeautifulSoup(response.text, "lxml")
    raw_text = soup.find("div", attrs={"id": "post-content-body"})
    # Теперь обработаем его через нейросеть
    if raw_text is None:
        return "Ошибка: не найдено содержимое статьи"
    text = raw_text.get_text(separator="\n", strip=True)
    return ask_model(text)


if __name__ == "__main__":

    new_links = habr_com_scraper()

    if new_links:
        with open(links_history_path, "a") as file:
            for link in new_links:
                file.write(link + "\n")
                logger.debug(f"Сохраняю ссылку в историю: {link}")

        for link in new_links:
            with open("texts.txt", 'a') as f:
                text = generate_telegram_post(link)
                f.write(text + "\n\n")

        logger.success("Все новые ссылки сохранены")
    else:
        logger.info("Нет новых подходящих ссылок")