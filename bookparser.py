import requests
import pandas as pd
import time
import random

CATEGORY = "fiction"  
BASE_URL = f"https://openlibrary.org/subjects/{CATEGORY}.json?limit=100&offset="
MAX_PAGES = 50
DELAY_RANGE = (1, 3)  
MAX_RUBRICS = 7  

RESULTS = []

def debug_print(data, label=""):
    """Функция для отладки"""
    if isinstance(data, dict):
        print(f"🔍 {label} JSON содержит ключи:", list(data.keys()))
    else:
        print(f"⚠️ Ошибка в {label}: JSON не является словарём")

def get_best_edition(book_key):
    """Берём самое информативное издание"""
    editions_url = f"https://openlibrary.org{book_key}/editions.json"
    editions_response = requests.get(editions_url)

    if editions_response.status_code != 200:
        return None

    editions_data = editions_response.json()
    if "entries" not in editions_data or not editions_data["entries"]:
        return None

    best_edition = max(editions_data["entries"], key=lambda e: len(e.keys()))
    debug_print(best_edition, "BEST EDITION")
    return best_edition

def get_book_details(book_key):
    """Получаем доп. инфо: страницы, язык, издателя, место публикации"""
    if not book_key:
        return "Нет данных", "Нет данных", "Нет данных", "Нет данных"

    url = f"https://openlibrary.org{book_key}.json"
    response = requests.get(url)

    if response.status_code != 200:
        return "Нет данных", "Нет данных", "Нет данных", "Нет данных"

    data = response.json()
    debug_print(data, "WORK")  

    # ✅ 1. Берём язык
    languages = data.get("languages", [])
    work_language = ", ".join([lang["key"].replace("/languages/", "") for lang in languages]) if languages else "Нет данных"

    # ✅ 2. Берём страницы
    pages = data.get("number_of_pages", "Нет данных")

    # ✅ 3. Если данных нет → ищем в edition
    best_edition = get_best_edition(book_key)

    publisher = "Нет данных"
    publish_place = "Нет данных"
    
    if best_edition:
        # ✅ 4. Проверяем язык в edition
        edition_languages = best_edition.get("languages", [])
        edition_language = ", ".join([lang["key"].replace("/languages/", "") for lang in edition_languages]) if edition_languages else "Нет данных"

        translated_from = best_edition.get("translated_from", [])
        if translated_from:
            translated_language = ", ".join([lang["key"].replace("/languages/", "") for lang in translated_from])
            edition_language = f"{edition_language}, {translated_language}" if edition_language != "Нет данных" else translated_language

        language = work_language if work_language != "Нет данных" else edition_language

        # ✅ 5. Проверяем "number_of_pages"
        if pages == "Нет данных":
            pages = best_edition.get("number_of_pages", "Нет данных")

        if pages == "Нет данных":
            pagination = best_edition.get("pagination", "Нет данных")
            if pagination != "Нет данных":
                pages = pagination.replace(" p.", "").replace(" pages", "")

        # ✅ 6. Издатель
        publishers = best_edition.get("publishers", [])
        publisher = ", ".join(publishers) if publishers else "Нет данных"

        # ✅ 7. Место публикации (фикс бага)
        publish_places = best_edition.get("publish_places", [])
        if isinstance(publish_places, list) and len(publish_places) > 0:
            publish_place = ", ".join([place for place in publish_places if isinstance(place, str)])
        if not publish_place or publish_place == "Нет данных":
            publish_place = data.get("publish_places", ["Нет данных"])[0]

    # ✅ 8. Жанры (subjects)
    subjects = data.get("subjects", [])[:MAX_RUBRICS]
    genres = ", ".join(subjects) if subjects else "Нет данных"
   

    return pages, language, publisher, publish_place, genres

def scrape_page(offset, book_id):
    """Парсинг одной страницы с книгами"""
    url = f"{BASE_URL}{offset}"
    print(f"🚀 Скрапинг {url}...")

    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Ошибка {response.status_code} на {url}")
        return book_id

    data = response.json()
    books = data.get("works", [])

    if not books:
        print("⚠️ Книги не найдены, возможно, изменился формат API.")
        return book_id

    for book in books:
        try:
            title = book.get("title", "Без названия")
            author = book["authors"][0]["name"] if book.get("authors") else "Неизвестный автор"
            year = book.get("first_publish_year", "Нет данных")
            book_key = book.get("key", None)
            link = f"https://openlibrary.org{book_key}" if book_key else "Нет ссылки"
            editions = book.get("edition_count", "Нет данных")
            cover_url = f"https://covers.openlibrary.org/b/id/{book['cover_id']}-L.jpg" if book.get("cover_id") else "Нет обложки"
            
            # ✅ Дополнительные данные
            pages, language, publisher, publish_place, genres = get_book_details(book_key)

            print(f"✅ {book_id}. {title} ({year}) - {author} | {pages} стр. | {language} | {genres} | Издатель: {publisher} | Публикация: {publish_place}")
            RESULTS.append({
                "ID": book_id,
                "Название": title,
                "Автор": author,
                "Год": year,
                "Ссылка": link,
                "Изданий": editions,
                "Страниц": pages,
                "Язык": language,
                "Издатель": publisher,
                "Место публикации": publish_place,
                "Жанры": genres,
                "Обложка": cover_url
            })
            book_id += 1  
        except Exception as e:
            print(f"❌ Ошибка парсинга книги: {e}")

    return book_id

def save_data():
    """Сохраняем данные в JSON, Excel и CSV"""
    if RESULTS:
        df = pd.DataFrame(RESULTS)
        df = df.drop_duplicates()

        df.to_json("opeenlibrary_books.json", orient="records", force_ascii=False, indent=4)
        df.to_excel("opeenlibrary_books.xlsx", index=False)
        df.to_csv("opeenlibrary_books.csv", index=False, encoding="utf-8-sig")

        print(f"\n✅ Данные сохранены! Книг собрано: {len(df)}")
    else:
        print("\n❌ Ошибка: данных нет, проверь OpenLibrary!")

def scrape_all():
    """Парсим 5000+ книг"""
    book_id = 1
    for page in range(MAX_PAGES):
        offset = page * 100
        book_id = scrape_page(offset, book_id)
        time.sleep(random.randint(*DELAY_RANGE))

    save_data()

# Запуск парсинга
scrape_all()