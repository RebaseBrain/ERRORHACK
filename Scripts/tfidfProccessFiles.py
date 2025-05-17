from joblib import load
import numpy as np
import json
import re
import os
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_distances
from scipy import sparse

COMMON_NOISE = ['usr', 'src', 'tmp', 'lib', 'lib64', 'site-packages']
CUSTOM_STOPWORDS = ['checking', 'found', 'alt', 'rpm', 'rpmi', 'linux', 'test', 'tests', 'sisyphus']

class Errors:
    def __init__(self, namepackage, errortype, pathToLogFile, nameCluster):
        self.namepackage = namepackage
        self.errortype = errortype
        self.pathToLogFile = pathToLogFile
        self.nameCluster = nameCluster

    def to_dict(self):
        return {
            "namepackage": self.namepackage,
            "errortype": self.errortype,
            "pathToLogFile": self.pathToLogFile,
		    "nameCluster": self.nameCluster
        }

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

def load_cluster_model():
    vectorizer = load('./Scripts/vectorizer.joblib')
    model = load('./Scripts/hdbscan_model.joblib')
    with open('./Scripts/cluster_keywords.json', 'r') as f:
        cluster_keywords = json.load(f)
    X_ref = sparse.load_npz('./Scripts/X_reference.npz')
    return vectorizer, model, cluster_keywords, X_ref

def find_nearest_cluster(text_input, vectorizer, model, X_ref):
    vec = vectorizer.transform([text_input])
    vec_norm = normalize(vec)
    X_ref_norm = normalize(X_ref)

    distances = cosine_distances(vec_norm, X_ref_norm)
    nearest_idx = distances[0].argmin()
    return model.labels_[nearest_idx]

def get_top_terms(text, vectorizer, top_n=5):
    tfidf_vector = vectorizer.transform([text])
    terms = vectorizer.get_feature_names_out()
    row = tfidf_vector[0].tocoo()

    term_scores = [(terms[i], v) for i, v in zip(row.col, row.data)]
    top_terms = sorted(term_scores, key=lambda x: -x[1])[:top_n]
    return [term for term, _ in top_terms]

if __name__ == "__main__":
    vectorizer, model, cluster_keywords, X_ref = load_cluster_model()

    log_dir = "./errors/"
    output_path = "./list_data.json"
    errs = []

    for filename in os.listdir(log_dir):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(log_dir, filename)

        with open(filepath, encoding='utf-8', errors='ignore') as f:
            content = preprocess_text(f.read())
            if not content:
                continue

            cluster_id = find_nearest_cluster(content, vectorizer, model, X_ref)

            if cluster_id == -1:
                keywords = get_top_terms(content, vectorizer, top_n=5)
            else:
                keywords = cluster_keywords.get(str(cluster_id), ["unknown"])

            err = Errors(
                namepackage=filename,
                errortype=", ".join(keywords),
                pathToLogFile=os.path.join("./logs", filename)
            )
            errs.append(err)

    with open(output_path, 'w') as f:
        json.dump([e.to_dict() for e in errs], f, indent=2)

    print(f"Сохранено: {output_path} ({len(errs)} записей)")
