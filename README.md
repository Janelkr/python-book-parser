# python-book-parser
Python-парсер для сбора информации о книгах с OpenLibrary API. Поддерживает JSON, CSV, XLSX

### 📝 Описание

Этот парсер собирает данные о книгах из OpenLibrary API, позволяя находить книги по категории, и собирает информацию: название книги, автор, год, ссылка, количество изданий, страниц, язык, издатель, место публикации, жанры, ссылка на обложку. Подходит для аналитики, рекомендаций и автоматизированного сбора информации.

### 🔹 Функционал

✅ Поиск книг по категории
✅ Сбор информации
✅ Сохранение информации в JSON, CSV, XLSX

### 📜 Используемые технологии

- **Язык программирования:** Python  
- **Библиотеки:** requests, pandas, json, time, random  


### 🚀 Установка и запуск

#### **3️⃣ Вывод результатов**

Парсер сохраняет найденные книги в три формата:

- **JSON** → `data/results.json`
- **CSV** → `data/results.csv`
- **Excel (XLSX)** → `data/results.xlsx`

Файлы можно открыть так:

```bash
cat data/results.xlsx  # Просмотр XLSX-результатов (Linux/macOS)
type data
esults.xlsx  # Просмотр XLSX-результатов (Windows)

cat data/results.json  # Просмотр JSON-результатов (Linux/macOS)
type data
esults.json  # Просмотр JSON-результатов (Windows)

cat data/results.csv  # Просмотр CSV-результатов (Linux/macOS)
type data
esults.csv  # Просмотр CSV-результатов (Windows)
```

#### **1️⃣ Установка зависимостей**

```bash
pip install requests
```

#### **2️⃣ Запуск парсера**

```bash
python parser.py "Название книги"
```

### 📂 Структура проекта

```
python-book-parser/
│
├── parser.py                      # Код парсера
├── data/                           # Папка с результатами парсинга
│   ├── results.json                # JSON-файл с результатами
│   ├── results.csv                 # CSV-файл с результатами
│   ├── results.xlsx                 # XLSX-файл с результатами
└── README.md
```




