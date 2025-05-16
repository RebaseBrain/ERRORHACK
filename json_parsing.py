import json
import os
from tabulate import tabulate

JSON_PATH = os.path.expanduser("~/data/build_errors.json")

def main():
    if not os.path.exists(JSON_PATH):
        print(f"[Ошибка] Файл не найден: {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[Ошибка] Неверный формат JSON: {e}")
            return

    table = []
    headers = ["Namepackage", "Error Type", "Package Type", "Path"]

    for item in data:
        row = [
            item.get("namepackage", "-"),
            item.get("errorType", "-"),
            item.get("packageType", "-"),
            item.get("pathToLogFile", "-")
        ]
        table.append(row)

    # Выводим таблицу
    print(tabulate(table, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()
