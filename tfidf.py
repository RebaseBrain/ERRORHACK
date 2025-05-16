import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from collections import defaultdict

# --- 1. Улучшенная предобработка ---


def preprocess_text(text):
    text = re.sub(r'\b\d+\.\d+\.\d+\b', '', text)  # Версии пакетов
    text = re.sub(r'\/\w+\/\w+\.\w+', '', text)    # Пути (/path/to/file.py)
    text = re.sub(r'\b[0-9a-f]{8}\b', '', text)    # Хэши (e.g., git commits)
    text = re.sub(r'\[.*?\]', '', text)            # [ERROR], [WARNING]
    return text.strip()

# --- 2. Кластеризация ошибок ---


def cluster_logs(texts, n_clusters=10):
    vectorizer = TfidfVectorizer(
        min_df=5,
        max_df=0.9,
        max_features=1000,
        ngram_range=(1, 3),
        stop_words='english'
    )
    X = vectorizer.fit_transform(texts)
# Удаляем слишком редкие/частые слова

    # Кластеризация
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X)

    # Извлечение ключевых слов для кластеров
    terms = vectorizer.get_feature_names_out()
    cluster_keywords = {}
    for i in range(n_clusters):
        cluster_center = kmeans.cluster_centers_[i]
        top_indices = cluster_center.argsort()[-20:][::-1]  # Топ-10 слов
        cluster_keywords[i] = [terms[ind] for ind in top_indices]

    return clusters, cluster_keywords, vectorizer, kmeans

# --- 3. Анализ новых ошибок ---


def analyze_error(text, vectorizer, kmeans):
    X = vectorizer.transform([text])
    cluster = kmeans.predict(X)[0]
    return cluster

# --- 4. Визуализация ---


def plot_clusters(X, clusters, keywords):
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X.toarray())

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(X_2d[:, 0], X_2d[:, 1],
                          c=clusters, cmap='viridis', alpha=0.6)
    plt.title('Кластеризация ошибок')
    plt.colorbar(scatter)

    # Аннотации с ключевыми словами
    for i, keywords in keywords.items():
        x, y = np.median(X_2d[clusters == i], axis=0)
        plt.annotate(
            f"Cluster {i}:\n{', '.join(keywords[:3])}...",
            (x, y), fontsize=8, ha='center'
        )
    plt.show()


# --- Основной поток ---
if __name__ == "__main__":
    # 1. Загрузка логов
    log_dir = "./Parser/logs/"
    texts = []
    for filename in os.listdir(log_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(log_dir, filename), 'r', encoding='utf-8', errors='ignore') as f:
                text = preprocess_text(f.read())
                if text:
                    texts.append(text)

    # 2. Кластеризация
    clusters, cluster_keywords, vectorizer, kmeans = cluster_logs(
        texts, n_clusters=100)

    # 3. Вывод результатов
    # print("Обнаруженные типы ошибок:")
    # for cluster_id, keywords in cluster_keywords.items():
    #    print(f"\nКластер {cluster_id} (возможная причина):")
    #   print("Ключевые слова:", ", ".join(keywords[:5]))

    # 4. Анализ нового файла
    test_file = "test.txt"
    with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
        test_text = preprocess_text(f.read())
        cluster = analyze_error(test_text, vectorizer, kmeans)
        # print(f"\nФайл '{test_file}' относится к кластеру {cluster}:")
        print("Характерные слова:", ", ".join(cluster_keywords[cluster][:5]))

    # 5. Визуализация (опционально)
    # X = vectorizer.transform(texts)
    # plot_clusters(X, clusters, cluster_keywords)
