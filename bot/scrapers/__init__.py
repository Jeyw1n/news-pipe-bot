__all__ = ("scrape_posts",)
from .habr_scraper import habr_com_scraper, links_history_path, generate_telegram_post
from loguru import logger

def scrape_posts():
    new_links = habr_com_scraper()
    posts = []

    if new_links:
        with open(links_history_path, "a") as file:
            for link in new_links:
                file.write(link + "\n")
                logger.debug(f"Сохраняю ссылку в историю: {link}")

        for link in new_links:
            text = generate_telegram_post(link)
            posts.append(text)

    return posts