# RebaseBrains Bugsniffer

# Содержание

- [Установка зависимостей](#Установка-зависимостей)
- [Запуск](#Запуск)
## Установка зависимостей
**Нужные пакеты**
- dotnet-runtime-8.0
- dotnet-sdk-8.0
- aspnet-runtime-8.0
- python3
- python3.12-venv
**Установка ollama**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
**Установка ollama**
```bash
ollama pull qwen3:0.6b
```
**Установка python библиотек**
- Создайте venv
- Запустите venv
- Установите библиотеки командой ниже
```bash
pip install torch ollama scikit-learn transformers sentencepiece scipy hdbscan numpy joblib
```

## Запуск
```bash
chmod +x main.sh
./main.sh
```
