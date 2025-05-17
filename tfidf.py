import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.feature_extraction import text
import json
from joblib import dump

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
        max_df=0.5,
        min_df=2
    )
    X = vectorizer.fit_transform(texts)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X)

    terms = vectorizer.get_feature_names_out()
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    cluster_keywords = {}

    X_dense = X.tocsc()

    for i in range(n_clusters):
        cluster_docs = np.where(kmeans.labels_ == i)[0]

        top_indices = order_centroids[i][:30]
        real_terms = []
        for ind in top_indices:
            col = X_dense[:, ind]
            if col[cluster_docs].nnz > 0:
                real_terms.append(terms[ind])
            if len(real_terms) == 10:
                break

        cluster_keywords[i] = real_terms

    return clusters, cluster_keywords, vectorizer, kmeans


def analyze_error(text, vectorizer, kmeans):
    X = vectorizer.transform([text])
    cluster = kmeans.predict(X)[0]
    return cluster


def plot_clusters(X, clusters, keywords):
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X.toarray())

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(X_2d[:, 0], X_2d[:, 1],
                          c=clusters, cmap='viridis', alpha=0.6)
    plt.title('Кластеризация ошибок')
    plt.colorbar(scatter)

    for i, keywords in keywords.items():
        x, y = np.median(X_2d[clusters == i], axis=0)
        plt.annotate(
            f"Cluster {i}:\n{', '.join(keywords[:3])}...",
            (x, y), fontsize=8, ha='center'
        )
    plt.show()


if __name__ == "__main__":
    log_dir = "./Parser/logs/"
    texts = []
    for filename in os.listdir(log_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(log_dir, filename), 'r', encoding='utf-8', errors='ignore') as f:
                text = preprocess_text(f.read())
                if text:
                    texts.append(text)

    clusters, cluster_keywords, vectorizer, kmeans = cluster_logs(
        texts, n_clusters=67)

    # Сохраняем модель, векторайзер и ключевые слова
    dump(vectorizer, 'vectorizer.joblib')
    dump(kmeans, 'kmeans_model.joblib')
    with open('cluster_keywords.json', 'w') as f:
        json.dump(cluster_keywords, f)
