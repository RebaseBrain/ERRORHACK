#!/bin/bash

green="\033[1;32m"
blue="\033[1;34m"
red="\033[1;31m"
reset="\033[0m"

printBanner() {
	echo -e "${green}╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮"
	echo -e "${green}│                  bbb                                 bbb                          ii                     │${reset}"
	echo -e "${green}│                   bb                                  bb                                                 │${reset}"
	echo -e "${green}│ r rrrr    eeee    bb       aaaa     sssss    eeee     bb      rrrrrr    aaaa     iii     nnnnn     sssss │${reset}"
	echo -e "${green}│ rr  rr  ee  ee    bbbbb       aa   ss       ee  ee    bbbbb    rr  rr      aa     ii     nn  nn   ss     │${reset}"
	echo -e "${green}│ rr      eeeeee    bb  bb   aaaaa    sssss   eeeeee    bb  bb   rr       aaaaa     ii     nn  nn    sssss │${reset}"
	echo -e "${green}│ rr      ee        bb  bb  aa  aa        ss  ee        bb  bb   rr      aa  aa     ii     nn  nn        ss│${reset}"
	echo -e "${green}│ rr       eeeee   bbbbbb    aaaaa   ssssss    eeeee   bbbbbb   rrrr      aaaaa    iiii    nn  nn   ssssss │${reset}"
	echo -e "${green}│                                                                                                          │${reset}"
	echo -e "${green}├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤${reset}"
	echo -e "${green}│    bbb                                            ii       fff      fff                                  │${reset}"
	echo -e "${green}│     bb                                                    ff ff    ff ff                                 │${reset}"
	echo -e "${green}│     bb      uu  uu    ggggg    sssss   nnnnn     iii      ff       ff       eeee    rrrrrr               │${reset}"
	echo -e "${green}│     bbbbb   uu  uu   gg  gg   ss       nn  nn     ii     ffff     ffff     ee  ee    rr  rr              │${reset}"
	echo -e "${green}│     bb  bb  uu  uu   gg  gg    sssss   nn  nn     ii      ff       ff      eeeeee    rr                  │${reset}"
	echo -e "${green}│     bb  bb  uu  uu    ggggg        ss  nn  nn     ii      ff       ff      ee        rr                  │${reset}"
	echo -e "${green}│    bbbbbb    uuuuuu      gg   ssssss   nn  nn    iiii    ffff     ffff      eeeee   rrrr                 │${reset}"
	echo -e "${green}│                       ggggg                                                                              │${reset}"
	echo -e "${green}╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯${reset}"
}

is_project_built() {
    dotnet_output=$(find ./Parser/bin/Debug -type f -name Parser.dll 2>/dev/null)
    [[ -n "$dotnet_output" ]]
}

printBanner

if !(is_project_built); then
	echo -e "${blue}Компиляция парсера...${reset}"
	dotnet build ./Parser/Parser.csproj
fi

# Меню выбора
echo -e "${blue}Выберите действие:${reset}"
echo -e "${green}[1]${reset} — собрать и обработать новые логи"
echo -e "${green}[2]${reset} — обработать логи"
echo -e "${green}[3]${reset} — обновить кластеры и обработать логи"
echo -e "${green}[4]${reset} — отмена"

read -p "> " user_choice

case "$user_choice" in
	1)
		echo -e "${blue}Сборка логов...${reset}"
		mkdir logs
		mkdir errors
		dotnet run --project ./Parser/Parser.csproj
		python3 ./Scripts/tfidf1.py
		python3 ./Scripts/tfidfProccessFiles.py
		python3 ./Scripts/parse.py
		;;
	2)
		echo -e "${blue}Обработка логов...${reset}"
		python3 ./Scripts/tfidfProccessFiles.py
		python3 ./Scripts/parse.py
		;;
	3)
		echo -e "${blue}Обновление кластеров...${reset}"
		python3 ./Scripts/tfidf1.py
		echo -e "${blue}Обработка логов...${reset}"
		python3 ./Scripts/tfidfProccessFiles.py
		python3 ./Scripts/parse.py
		;;
	4)
		echo -e "${blue}Отмена.${reset}"
		exit 0;
		;;
	*)
		echo -e "${red}Некорректный ввод. Завершение.${reset}"
		exit 1
		;;
esac

