import ollama
import json

def get_error_category(error_list):
    errors_str = ", ".join(error_list)
    prompt = f"""
	A comma-separated error string is given: '{errors_str}'. 
    Name this group of errors with 1-3 words. Only group name, don't write explanation:
	"""
    
    response = ollama.generate(
        model="qwen:1.7b",  # или "qwen:0.6b"
        prompt=prompt,
        options={
			"temperature": 0.1,
			#"stop": ["\n"]
		}  # Для более предсказуемых результатов
    )
    
    return response["response"].strip()

# Пример использования
errors = [
    "uses non",
    "verify elf error",
    "elf error",
    "uses non lfs",
    "non lfs functions",
    "uses non lfs functions",
    "lfs functions",
    "non lfs",
    "verify elf",
    "elf error bin"
  ]
category = get_error_category(errors)
file_path="./test.json"
with open(file_path, "w", encoding="utf-8") as file:
	json.dump(category, file);
