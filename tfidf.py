import os
import re
import numpy as np
from transformers import AutoTokenizer, AutoModelimport 
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.feature_extraction import text
import json
from joblib import dump
from collections import Counter

LOG_DIR = "./Parser/errors/"
N_CLUSTERS = 67  # По умолчанию; можно заменить на автоопределение
VECTORIZER_PATH = "vectorizer.joblib"
KMEANS_PATH = "kmeans_model.joblib"
KEYWORDS_PATH = "cluster_keywords.json"
CLUSTER_MAP_PATH = "cluster_map.json"

COMMON_NOISE = ['usr', 'src', 'tmp', 'lib', 'lib64', 'site-packages']
CUSTOM_STOPWORDS = ['checking', 'found', 'alt', 'rpm', 'rpmi', 'linux', 'test', 'tests', 'sisyphus']

def preprocess_text(text_raw):
	text_raw = text_raw.lower()
	text_raw = re.sub(r'\b\d+\.\d+\.\d+\b', '', text_raw)
	text_raw = re.sub(r'\/[\w\.-]+\/[\w\.-]+\.\w+', '', text_raw)
	text_raw = re.sub(r'\b[0-9a-f]{8,}\b', '', text_raw)
	text_raw = re.sub(r'\[.*?\]', '', text_raw)
	text_raw = re.sub(r'[^a-z\s]', ' ', text_raw)
	for word in COMMON_NOISE:
		text_raw = re.sub(rf'\b{word}\b', '', text_raw)
	text_raw = re.sub(r'\s+', ' ', text_raw)
	return text_raw.strip()


# --- 2. Кластеризация ошибок ---
all_stopwords = list(text.ENGLISH_STOP_WORDS.union(CUSTOM_STOPWORDS))

def get_log_embeddings(logs, batch_size=4):
	embeddings = []
	for i in range(0, len(logs), batch_size):
		batch = logs[i:i + batch_size]
		inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
		with torch.no_grad():
			outputs = model(**inputs)
		batch_embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
		embeddings.append(batch_embeddings)
	return np.vstack(embeddings)

def cluster_logs(texts, n_clusters=N_CLUSTERS):
	vectorizer = TfidfVectorizer(
		max_features=10000,
		ngram_range=(2, 4),
		stop_words=all_stopwords,
		max_df=0.5,
		min_df=2
	)
	X = vectorizer.fit_transform(texts)

	model_name = "deepseek-ai/deepseek-r1"
	tokenizer = AutoTokenizer.from_pretrained(model_name)
	model = AutoModel.from_pretrained(model_name)

	log_embeddings = get_log_embeddings(processed_logs)

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

	return clusters, cluster_keywords, vectorizer, kmeans, X

def analyze_error(text_input, vectorizer, kmeans):
	X = vectorizer.transform([text_input])
	cluster = kmeans.predict(X)[0]
	return cluster



# def plot_clusters(X, clusters, keywords):
#	 pca = PCA(n_components=2)
#	 X_2d = pca.fit_transform(X.toarray())
#
#	 plt.figure(figsize=(10, 6))
#	 scatter = plt.scatter(X_2d[:, 0], X_2d[:, 1],
#						   c=clusters, cmap='viridis', alpha=0.6)
#	 plt.title('Кластеризация ошибок')
#	 plt.colorbar(scatter)
#
#	 for i, keywords in keywords.items():
#		 x, y = np.median(X_2d[clusters == i], axis=0)
#		 plt.annotate(
#			 f"Cluster {i}:\n{', '.join(keywords[:3])}...",
#			 (x, y), fontsize=8, ha='center'
#		 )
#	 plt.show()


if __name__ == "__main__":
	texts = []
	filenames = []
	dropped = 0

	for filename in sorted(os.listdir(LOG_DIR)):
		if filename.endswith(".txt"):
			with open(os.path.join(LOG_DIR, filename), 'r', encoding='utf-8', errors='ignore') as f:
				text_content = preprocess_text(f.read())
				if text_content:
					texts.append(text_content)
					filenames.append(filename)
				else:
					dropped += 1

	print(f"Загружено файлов: {len(texts)} | Пропущено (пустых): {dropped}")

	clusters, cluster_keywords, vectorizer, kmeans, X = cluster_logs(texts, n_clusters=N_CLUSTERS)

	print("\nРаспределение по кластерам:")
	for cluster_id, count in sorted(Counter(clusters).items()):
		print(f"  Кластер {cluster_id}: {count} файлов")

	cluster_map = {filenames[i]: int(clusters[i]) for i in range(len(filenames))}

	# Сохранение
	dump(vectorizer, VECTORIZER_PATH)
	dump(kmeans, KMEANS_PATH)
	with open(KEYWORDS_PATH, 'w') as f:
		json.dump(cluster_keywords, f, indent=2)
	with open(CLUSTER_MAP_PATH, 'w') as f:
		json.dump(cluster_map, f, indent=2)

	print("\nСохранены:")
	print(f"  Векторайзер → {VECTORIZER_PATH}")
	print(f"  Модель KMeans → {KMEANS_PATH}")
	print(f"  Ключевые слова кластеров → {KEYWORDS_PATH}")
	print(f"  Сопоставление файлов → кластеров → {CLUSTER_MAP_PATH}")


