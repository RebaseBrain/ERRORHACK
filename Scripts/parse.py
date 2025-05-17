import json
import os

def parse_json(pathToJSON):
    with open(pathToJSON, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def aboba_sort(data, nameCluster):
    return [item for item in data if item["nameCluster"] == nameCluster]

if __name__ == '__main__':
    data = parse_json('./list_data.json')

    # Загружаем карту названий кластеров
    with open('./Scripts/cluster_name_map.json', 'r', encoding='utf-8') as f:
        cluster_name_map = json.load(f)

    # Получаем уникальные ID кластеров
    all_cluster_ids = list(set([item["nameCluster"] for item in data]))

    os.makedirs("./clusters", exist_ok=True)

    for cluster_id in all_cluster_ids:
        group = aboba_sort(data, cluster_id)

        # Получаем имя кластера из карты названий
        name = cluster_name_map.get(str(cluster_id), f"cluster_{cluster_id}")
        filename_safe = name.replace(" ", "+").replace("/", "_")

        with open(f"./clusters/{filename_safe}.json", "w", encoding="utf-8") as f:
            json.dump(group, f, indent=2, ensure_ascii=False)

        print(f"Сохранено: ./clusters/{filename_safe}.json ({len(group)} файлов)")
