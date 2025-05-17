# RebaseBrains Bugsniffer

# Содержание

- [Установка зависимостей](#Установка-зависимостей)
- [Запуск](#Запуск)
- [Микро инфа](#Микро-инфа)
## Установка зависимостей
**Нужные пакеты**
- dotnet-runtime-8.0
- dotnet-sdk-8.0
- aspnet-runtime-8.0
- python3
- python3.12-venv

**Установка ollama Linux**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
**Установка ollama MacOS**

[MacOS ollama](https://ollama.com/download/Ollama-darwin.zip)

**Установка Qwen**
```bash
ollama pull qwen3:0.6b
```
**Установка python библиотек**
- Создайте venv
- Запустите venv
- Установите библиотеки командой ниже
```bash
echo "ollama
scikit-learn
sentencepiece
scipy
hdbscan
numpy
joblib" > requirements.txt
pip install -r requirements.txt
```

Python-у может не понравится установка нескольких зависимостей разом, в таком случае стоит скачать каждую библиотеку отдельно так:
```bash
pip install ollama # и так с каждой библиотекой
```

## Запуск
```bash
chmod +x main.sh
./main.sh
```

## Микро инфа
У нас неправильно выводятся id у кластеров при выборе (порядок id, то есть не 1, 2, 3..., а 1, 11, 12,..., 2, 21)
