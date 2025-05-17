import os
import re
import json
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.feature_extraction import text
from joblib import dump
from scipy import sparse
import hdbscan

# Пути
LOG_DIR = "./errors/"
HDBSCAN_PATH = "./Scripts/hdbscan_model.joblib"
VECTORIZER_PATH = "./Scripts/vectorizer.joblib"
KEYWORDS_PATH = "./Scripts/cluster_keywords.json"
CLUSTER_MAP_PATH = "./Scripts/cluster_map.json"
X_MATRIX_PATH = "./Scripts/X_reference.npz"

# Стоп-слова
COMMON_NOISE = ['usr', 'src', 'tmp', 'lib', 'lib64', 'site-packages']
CUSTOM_STOPWORDS = ['checking', 'found', 'alt', 'rpm', 'rpmi', 'linux', 'test', 'tests', 'sisyphus']
all_stopwords = list(text.ENGLISH_STOP_WORDS.union(CUSTOM_STOPWORDS))

def remove_repeated_sequences(text, max_ngram=4):
    words = text.split()
    cleaned = []
    i = 0
    while i < len(words):
        repeated = False
        for n in range(max_ngram, 1, -1):
            if i + 2 * n <= len(words):
                first = words[i:i + n]
                second = words[i + n:i + 2 * n]
                if first == second:
                    repeated = True
                    i += n
                    break
        if not repeated:
            if cleaned and words[i] == cleaned[-1]:
                i += 1
                continue
            cleaned.append(words[i])
            i += 1
    return ' '.join(cleaned)

# Очистка текста
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\b\d+\.\d+\.\d+\b', '', text)
    text = re.sub(r'\/[\w\.-]+\/[\w\.-]+\.\w+', '', text)
    text = re.sub(r'\b[0-9a-f]{8,}\b', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    for word in COMMON_NOISE:
        text = re.sub(rf'\b{word}\b', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = remove_repeated_sequences(text, max_ngram=4)
    return text.strip()

# Извлечение ключевых слов для каждого кластера
def extract_keywords(X, labels, vectorizer, top_n=10):
    terms = vectorizer.get_feature_names_out()
    X_dense = X.tocsc()
    cluster_keywords = {}

    for cluster_id in sorted(set(labels)):
        if cluster_id == -1:
            continue
        doc_indices = np.where(labels == cluster_id)[0]
        sub_matrix = X[doc_indices]
        mean_tfidf = np.asarray(sub_matrix.mean(axis=0)).flatten()
        top_indices = mean_tfidf.argsort()[::-1]

        keywords = []
        for idx in top_indices:
            col = X_dense[:, idx]
            if col[doc_indices].nnz > 0:
                keywords.append(terms[idx])
            if len(keywords) == top_n:
                break

        cluster_keywords[int(cluster_id)] = keywords

    return cluster_keywords

if __name__ == "__main__":
    texts = []
    filenames = []

    for filename in sorted(os.listdir(LOG_DIR)):
        if filename.endswith(".txt"):
            with open(os.path.join(LOG_DIR, filename), 'r', encoding='utf-8', errors='ignore') as f:
                content = preprocess_text(f.read())
                if content:
                    texts.append(content)
                    filenames.append(filename)

    print(f"Загружено логов: {len(texts)}")

    # Векторизация
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(2, 4),
        stop_words=all_stopwords,
        max_df=0.5,
        min_df=2
    )
    X = vectorizer.fit_transform(texts)
    X_norm = normalize(X)

    # Обучаем HDBSCAN
    clusterer = hdbscan.HDBSCAN(min_cluster_size=3, metric='euclidean')
    clusterer.fit(X_norm)
    labels = clusterer.labels_

    # Ключевые слова для кластеров
    cluster_keywords = extract_keywords(X, labels, vectorizer)

    # Сопоставление файлов → кластеров
    cluster_map = {filenames[i]: int(labels[i]) for i in range(len(filenames))}

    print("\nРаспределение по кластерам:")
    for cl_id, count in sorted(Counter(labels).items()):
        print(f"  Кластер {cl_id}: {count} файлов")

    # Сохранение
    dump(vectorizer, VECTORIZER_PATH)
    dump(clusterer, HDBSCAN_PATH)
    with open(KEYWORDS_PATH, 'w') as f:
        json.dump(cluster_keywords, f, indent=2)
    with open(CLUSTER_MAP_PATH, 'w') as f:
        json.dump(cluster_map, f, indent=2)
    sparse.save_npz(X_MATRIX_PATH, X)

    print("\nСохранено:")
    print(f"  Векторайзер       → {VECTORIZER_PATH}")
    print(f"  Модель HDBSCAN    → {HDBSCAN_PATH}")
    print(f"  Ключевые слова    → {KEYWORDS_PATH}")
    print(f"  Сопоставления     → {CLUSTER_MAP_PATH}")
    print(f"  X (TF-IDF)        → {X_MATRIX_PATH}")
