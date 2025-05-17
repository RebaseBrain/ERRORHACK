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

printBanner

sleep 1
echo -e "${blue}Analyzing Code...${reset}"
sleep 1

# Prompt user to choose format
read -p "Choose output format [csv/tsv]: " output_format
while [[ ! "$output_format" =~ ^(csv|tsv)$ ]]; do
  read -p "Invalid choice. Choose [csv/tsv]: " output_format
done

# Set delimiter based on format
delimiter=$'\t'
if [[ "$output_format" == "csv" ]]; then
  delimiter=","
fi

# Output file in project root
output_file="build_errors.$output_format"

# Write headers (all fields)
echo "${red}namepackage${delimiter}errorType${delimiter}pathToLogFile${delimite}" > "$output_file"

# Use jq with sub() instead of gsub() for compatibility
jq -r --arg delim "$delimiter" '.[] | [
    .namepackage,
    .errorType,
    (.pathToLogFile | sub("\\\\"; "/"; "g")),
  ] | join($delim)' "$json_path" >> "$output_file"

# Display the table
column -s "$delimiter" -t < "$output_file" | less -S
