from joblib import load
import json
import re
import os
COMMON_NOISE = ['usr', 'src', 'tmp', 'lib', 'lib64', 'site-packages']
CUSTOM_STOPWORDS = ['checking', 'found', 'notfound']


class Errors:
    namepackage = ""
    errortype = ""
    pathToLogFile = ""

    def __init__(self, namepackage, errortype, pathToLogFile):
        # Атрибут экземпляра (уникальный для каждого объекта)
        self.namepackage = namepackage
        self.errortype = errortype
        self.pathToLogFile = pathToLogFile

    def to_dict(self):
        return {
            "namepackage": self.namepackage,
            "errortype": self.errortype,
            "pathToLogFile": self.pathToLogFile
        }


def analyze_error(text, vectorizer, kmeans):
    X = vectorizer.transform([text])
    cluster = kmeans.predict(X)[0]
    return cluster


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


def load_cluster_model():
    vectorizer = load('vectorizer.joblib')
    kmeans = load('kmeans_model.joblib')
    with open('cluster_keywords.json', 'r') as f:
        cluster_keywords = json.load(f)
    return vectorizer, kmeans, cluster_keywords


if __name__ == "__main__":
    # Загружаем сохраненную модель
    vectorizer, kmeans, cluster_keywords = load_cluster_model()

    log_dir = "./Parser/errors/"
    errs = []
    for filename in os.listdir(log_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(log_dir, filename)) as f:
                test_text = preprocess_text(f.read())
                cluster = analyze_error(test_text, vectorizer, kmeans)
                # texts[filename] = ", ".join(cluster_keywords[str(cluster)][:5])
                errortype = ", ".join(cluster_keywords[str(cluster)][:5])
                pathToLogFile = os.path.join("./Parser/logs", filename)
                errs.append(Errors(filename, errortype, pathToLogFile))

    with open('Parser/list_data.json', 'w') as f:
        for err in errs:
            json.dump(err.to_dict(), f, indent=2)
    # Анализируем новый файл
    # test_file = "test.txt"
    # with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
    #     test_text = preprocess_text(f.read())
    #     cluster = analyze_error(test_text, vectorizer, kmeans)
    #     print(f"\nФайл '{test_file}' относится к кластеру {cluster}:")
    #     print("Характерные слова:", ", ".join(
    #         cluster_keywords[str(cluster)][:5]))
