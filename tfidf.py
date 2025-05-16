import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction import text

# --- 1. Улучшенная предобработка ---

# COMMON_NOISE = ['usr', 'src', 'tmp', 'build', 'lib', 'lib64', 'bin', 'site-packages', 'rpm', 'python3']
#
# CUSTOM_STOPWORDS = [
#     'cmake' 'make', 'gcc', 'build', 'check', 'checking',
#     'warning', 'error', 'configure', 'file', 'line',
#     'install', 'run', 'test', 'pass', 'fail', 'script',
#     'include', 'lib', 'package', 'found', 'notfound'
# ]

COMMON_NOISE = ['usr', 'src', 'tmp', 'lib', 'lib64', 'site-packages']
CUSTOM_STOPWORDS = ['checking', 'found', 'notfound']

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\b\d+\.\d+\.\d+\b', '', text)  # Версии пакетов
    text = re.sub(r'\/[\w\.-]+\/[\w\.-]+\.\w+', '', text)  # Пути /xxx/yyy.zzz
    text = re.sub(r'\b[0-9a-f]{8,}\b', '', text)  # Хэши
    text = re.sub(r'\[.*?\]', '', text)  # [ERROR], [INFO]
    text = re.sub(r'[^a-z\s]', ' ', text)  # Удалить все не-буквы
    for word in COMMON_NOISE:
        text = re.sub(rf'\b{word}\b', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# --- 2. Кластеризация ошибок ---
all_stopwords = list(text.ENGLISH_STOP_WORDS.union(CUSTOM_STOPWORDS))
def cluster_logs(texts, n_clusters=5):
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(2, 3),
        stop_words=all_stopwords,
        max_df=0.5,  # Игнорировать слишком частые
        min_df=2     # Игнорировать слишком редкие
    )
    X = vectorizer.fit_transform(texts)

    # Кластеризация
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X)

    # Извлечение ключевых слов для кластеров
    terms = vectorizer.get_feature_names_out()
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    cluster_keywords = {}

    X_dense = X.tocsc()  # Для эффективного доступа к колонкам (т.е. признакам)

    for i in range(n_clusters):
        # Индексы документов текущего кластера
        cluster_docs = np.where(kmeans.labels_ == i)[0]

        top_indices = order_centroids[i][:30]
        real_terms = []
        for ind in top_indices:
            # Проверка: есть ли хоть один документ этого кластера, где этот term ненулевой
            col = X_dense[:, ind]
            if col[cluster_docs].nnz > 0:
                real_terms.append(terms[ind])
            if len(real_terms) == 10:
                break

        cluster_keywords[i] = real_terms

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

# --- 5. Подбор наилучшего качества кластеризации ---
# def evaluate_k_range(texts, k_range=range(2, 100)):
#     vectorizer = TfidfVectorizer(
#         max_features=1000,
#         ngram_range=(1, 2),
#         stop_words=all_stopwords,
#         max_df=0.5,
#         min_df=2
#     )
#     X = vectorizer.fit_transform(texts)
#
#     inertias = []
#     silhouettes = []
#
#     for k in k_range:
#         kmeans = KMeans(n_clusters=k, random_state=42)
#         labels = kmeans.fit_predict(X)
#         inertias.append(kmeans.inertia_)
#         silhouettes.append(silhouette_score(X, labels))
#
#     # Построение графиков
#     fig, ax1 = plt.subplots(figsize=(10, 5))
#
#     ax1.set_xlabel("Количество кластеров k")
#     ax1.set_ylabel("Inertia (локоть)", color="tab:blue")
#     ax1.plot(k_range, inertias, marker='o', label="Inertia", color="tab:blue")
#     ax1.tick_params(axis='y', labelcolor="tab:blue")
#
#     ax2 = ax1.twinx()
#     ax2.set_ylabel("Silhouette Score", color="tab:orange")
#     ax2.plot(k_range, silhouettes, marker='s', label="Silhouette", color="tab:orange")
#     ax2.tick_params(axis='y', labelcolor="tab:orange")
#
#     fig.tight_layout()
#     plt.title("Выбор оптимального числа кластеров")
#     plt.grid(True)
#     plt.show()
#
#     # Вывод наилучшего k по силуэту
#     best_k = k_range[silhouettes.index(max(silhouettes))]
#     print(f"\nНаилучшее k по силуэту: {best_k} (score={max(silhouettes):.4f})")
#
#     return best_k

# --- Основной поток ---
if __name__ == "__main__":
    # 1. Загрузка логов
    log_dir = "./Parser/errors//"
    texts = []
    for filename in os.listdir(log_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(log_dir, filename), 'r', encoding='utf-8', errors='ignore') as f:
                text = preprocess_text(f.read())
                if text:
                    texts.append(text)

    # 2. Автоматический подбор числа кластеров
    # best_k = evaluate_k_range(texts, k_range=range(2, 100))

    # 3. Кластеризация с подобранным k
    clusters, cluster_keywords, vectorizer, kmeans = cluster_logs(
        texts, n_clusters=67)

    # 3. Вывод результатов
    print("Обнаруженные типы ошибок:")
    for cluster_id, keywords in cluster_keywords.items():
        print(f"\nКластер {cluster_id} (возможная причина):")
        print("Ключевые слова:", ", ".join(keywords[:5]))

    # 4. Анализ нового файла
    test_file = "test.txt"
    with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
        test_text = preprocess_text(f.read())
        cluster = analyze_error(test_text, vectorizer, kmeans)
        print(f"\nФайл '{test_file}' относится к кластеру {cluster}:")
        print("Характерные слова:", ", ".join(cluster_keywords[cluster][:5]))

    # 5. Визуализация (опционально)
    # X = vectorizer.transform(texts)
    # plot_clusters(X, clusters, cluster_keywords)
