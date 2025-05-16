#!/bin/bash

green="\033[1;32m"
blue="\033[1;34m"
red="\033[1;31m"
reset="\033[0m"
json_path="errors/main.json"

printBanner() {
	echo -e "${green}╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮"
	echo -e "${green}│                  bbb                                 bbb                          ii                     │${reset}"
	echo -e "${green}│                   bb                                  bb                                                 │${reset}"
	echo -e "${green}│   rrrr    eeee    bb       aaaa     sssss    eeee     bb      rrrrrr    aaaa     iii     nnnnn     sssss │${reset}"
	echo -e "${green}│ rr  rr  ee  ee    bbbbb       aa   ss       ee  ee    bbbbb    rr  rr      aa     ii     nn  nn   ss     │${reset}"
	echo -e "${green}│ rr      eeeeee    bb  bb   aaaaa    sssss   eeeeee    bb  bb   rr       aaaaa     ii     nn  nn    sssss │${reset}"
	echo -e "${green}│ rr      ee        bb  bb  aa  aa        ss  ee        bb  bb   rr      aa  aa     ii     nn  nn        ss│${reset}"
	echo -e "${green}│ rrrr     eeeee   bbbbbb    aaaaa   ssssss    eeeee   bbbbbb   rrrr      aaaaa    iiii    nn  nn   ssssss │${reset}"
	echo -e "${green}│                                                                                                          │${reset}"
	echo -e "${green}├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤${reset}"
	echo -e "${green}│    bbb                                            ii       fff      fff                                  │${reset}"
	echo -e "${green}│     bb                                                    ff ff    ff ff                                 │${reset}"
	echo -e "${green}│     bb      uu  uu    ggggg    sssss   nnnnn     iii       f        f       eeee    rrrrrr               │${reset}"
	echo -e "${green}│     bbbbb   uu  uu   gg  gg   ss       nn  nn     ii     ffff     ffff     ee  ee    rr  rr              │${reset}"
	echo -e "${green}│     bb  bb  uu  uu   gg  gg    sssss   nn  nn     ii      ff       ff      eeeeee    rr                  │${reset}"
	echo -e "${green}│     bb  bb  uu  uu    ggggg        ss  nn  nn     ii      ff       ff      ee        rr                  │${reset}"
	echo -e "${green}│    bbbbbb    uuuuuu      gg   ssssss   nn  nn    iiii    ffff     ffff      eeeee   rrrr                 │${reset}"
	echo -e "${green}│                       ggggg                                                                              │${reset}"
	echo -e "${green}╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯${reset}"
}

printBanner

sleep 1
echo -e "${blue}Analyzing Code...${reset}"
sleep 1

if [ ! -f "$json_path" ]; then
	echo "File $json_path not found!"
	exit 1
fi

echo -e "${red}namepackage\terrorType\tpackageType\tpathToLogFile${reset}" > /tmp/build_errors.tsv
jq -r '.[] | "\(.namepackage)\t(.errorType)\t\(.packageType)\t(.pathToLogFile)"' "$json_path" >> /tmp/build_errors.tsv

column -s $'\t' -t < /tmp/build_errors.tsv
