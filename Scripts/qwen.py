import json
import ollama
import os
import deleteBrain

def generate_cluster_name(keywords):
	prompt = (
		"Придумай короткое, осмысленное название (1-3 слова) "
		"для технической категории, используя следующие ключевые слова:\n"
		f"{keywords}\n"
		"Ответ должен содержать только название категории, без пояснений."
	)

	response = ollama.chat(
		model="qwen3:0.6b",
		messages=[{"role": "user", "content": prompt}]
	)
	raw_name = response['message']['content']
	clean_name = deleteBrain.delBrain(raw_name)
	return clean_name

def generate_all_cluster_names(path_to_keywords="./Scripts/cluster_keywords.json", output_path="./Scripts/cluster_name_map.json"):
	with open(path_to_keywords, "r", encoding="utf-8") as f:
		cluster_keywords = json.load(f)

	cluster_name_map = {}
	for cluster_id, keywords in cluster_keywords.items():
		name = generate_cluster_name(keywords)
		safe_name = name.replace(" ", "_")
		cluster_name_map[cluster_id] = safe_name
		print(f"Кластер {cluster_id} → {safe_name}")

	# Убедимся, что директория существует
	os.makedirs(os.path.dirname(output_path), exist_ok=True)

	with open(output_path, "w", encoding="utf-8") as f:
		json.dump(cluster_name_map, f, indent=2, ensure_ascii=False)

	return cluster_name_map

if __name__ == "__main__":
	generate_all_cluster_names()
