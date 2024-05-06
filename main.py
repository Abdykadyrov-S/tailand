import requests
from bs4 import BeautifulSoup
import os
import openai
import logging
from dotenv import load_dotenv
import config


# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

client = openai.OpenAI(
   api_key=config.openai_api_key
)

def get_full_article(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        article_text = soup.find('article')
        if article_text:
            return article_text.get_text(strip=True)
        else:
            return "Не удалось найти текст статьи."
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при загрузке страницы: {e}")
        return None

def rewrite_text_with_openai(text):
    try:
        response = client.chat.Completion.create(
            model="gpt-3.5-turbo",
            prompt=f"Перепиши статью, основанную на следующем тексте, с включением вводных абзацев, междузаголовков и заключения: '{text}'",
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Ошибка при вызове OpenAI: {e}")
        return None

def get_thailand_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "Thailand",
        "apiKey": config.news_api_Key
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "ok":
            articles = data["articles"]
            if not os.path.exists('thailand_text'):
                os.makedirs('thailand_text')

            for index, article in enumerate(articles):
                logging.info(f"Заголовок: {article['title']}")
                full_text = get_full_article(article['url'])
                
                if full_text:
                    rewritten_text = rewrite_text_with_openai(full_text)
                    if rewritten_text:
                        file_name = os.path.join('thailand_text', f'article_{index + 1}.txt')
                        with open(file_name, "w", encoding='utf-8') as file:
                            file.write(rewritten_text)
                        logging.info(f"Переформулированный текст сохранен в файле: {file_name}")
                else:
                    logging.info("Не удалось получить текст статьи.")
        else:
            logging.error(f"Ошибка при получении новостей: {data.get('message', 'Неизвестная ошибка')}")
    else:
        logging.error(f"Ошибка HTTP: {response.status_code}")

if __name__ == '__main__':
    get_thailand_news()
