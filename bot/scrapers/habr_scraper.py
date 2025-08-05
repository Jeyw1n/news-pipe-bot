import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger
import os

from .ai_formatter import ask_model


URL = "https://habr.com"
FILTERS = {
    "информационная безопасность",
    "информационная безопасность*"
}
headers = {"User-Agent": UserAgent().chrome}
links_history_path = os.path.join(
    os.path.dirname(__file__),
    f"history/{os.path.basename(__file__)[:-3]}_history.txt"
)


def get_links_history() -> list[str]:
    """ Возвращает списком историю полученных ссылок """
    if not os.path.isfile(links_history_path):
        logger.info(f"Файл \"{links_history_path}\" не существует.")
        return []
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
            text, image_prompt = generate_telegram_post(link)
            print(text + "\n" + image_prompt + "\n-----------\n\n")

        logger.success("Все новые ссылки сохранены")
    else:
        logger.info("Нет новых подходящих ссылок")