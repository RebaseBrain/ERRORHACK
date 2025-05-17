import json
import os

class error:
    enamepackage = ""
    errortype = ""
    pathToLogFile = ""
    nameCluster = ""

    def __init__(self, namepackage, errortype, pathToLogFile, nameCluster):
        self.namepackage = namepackage
        self.errortype = errortype
        self.pathToLogFile = pathToLogFile
        self.nameCluster = nameCluster

def parse_json(pathToJSON):
    with open(pathToJSON, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def aboba_sort(data, nameCluster):
    return [item for item in data if item["nameCluster"] == nameCluster]

if __name__ == '__main__':
    data = parse_json('./list_data.json')
    allTypes = list(set([item["nameCluster"] for item in data]))

    # Заменяем пробелы на + в nameCluster
    for item in data:
        item["nameCluster"] = item["nameCluster"].replace(" ", "+")

    allTypes = list(set([item["nameCluster"] for item in data]))

    # Создаём папку, если её нет
    os.makedirs("./clusters", exist_ok=True)

    for cluster_name in allTypes:
        cluster_items = aboba_sort(data, cluster_name)
        file_path = f"./clusters/{cluster_name}.json"
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(cluster_items, file, indent=2, ensure_ascii=False)
