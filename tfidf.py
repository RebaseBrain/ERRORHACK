import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier  # Если есть метки
from sklearn.svm import OneClassSVM  # Если меток нет (аномалии)
import numpy as np
import re

# --- 1. Загрузка и предобработка логов ---


def preprocess_text(text):
    # Удаляем даты, числа, спецсимволы (настраивайте под свои логи)
    text = re.sub(r'\d{4}-\d{2}-\d{2}', '', text)  # Даты вида 2023-01-01
    text = re.sub(r'\[.*?\]', '', text)  # [ERROR], [WARNING]
    text = re.sub(r'\w+\.\w+:\d+', '', text)  # file.py:123
    return text.strip()


def load_logs(directory):
    texts, filenames = [], []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            try:
                with open(os.path.join(directory, filename), 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                    if text.strip():  # Пропускаем пустые файлы
                        texts.append(preprocess_text(text))
                        filenames.append(filename)
            except Exception as e:
                print(f"Ошибка чтения {filename}: {e}")
    return texts, filenames


# --- 2. Обучение TF-IDF ---
log_dir = "./Parser/logs/"
texts, filenames = load_logs(log_dir)

if not texts:
    raise ValueError("Нет данных для обучения! Проверьте путь или файлы.")

vectorizer = TfidfVectorizer(
    max_features=500,
    stop_words='english',
    ngram_range=(1, 2),
    min_df=2  # Игнорировать редкие слова
)
X = vectorizer.fit_transform(texts)

# --- 3. Обучение модели ---
# Вариант 1: Если есть метки (ошибка/не ошибка)
# labels = [1, 0, 1, ...]  # 1 = ошибка, 0 = норма
# model = RandomForestClassifier().fit(X, labels)

# Вариант 2: Если меток нет (ищем аномалии)
model = OneClassSVM(nu=0.05)  # nu = % ожидаемых аномалий
model.fit(X)

# --- 4. Проверка нового файла ---


def check_for_errors(filepath, vectorizer, model, threshold=0):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = preprocess_text(f.read())
            if not text:
                return False, 0  # Пустой файл = не ошибка

            X_new = vectorizer.transform([text])
            prediction = model.predict(X_new)  # Для OneClassSVM: -1 = ошибка
            return prediction[0] == -1, prediction[0]
    except Exception as e:
        print(f"Ошибка при анализе {filepath}: {e}")
        return False, 0


# Пример использования
new_file = "test.txt"
is_error, score = check_for_errors(new_file, vectorizer, model)
print(f"Файл: {new_file}, Ошибка: {is_error}, Score: {score}")
