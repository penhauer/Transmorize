#!/bin/bash

from_lang=en
to_lang=fa


main_translation=[0][0][0]
usage=[1]

#  [1]
#  [0] [1] [2] ...
#  [0] -> usage
#  [1] -> usage list without equivalents
#  [2] -> list of usageus with equivalents

get_raw_translation() {
	url="https://translate.googleapis.com/translate_a/single?client=gtx&ie=UTF-8&oe=UTF-8&dt=bd&dt=ex&dt=ld&dt=md&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=gt&dt=qca&sl=${from_lang}&tl=${to_lang}&hl=en"
	curl -G --data-urlencode q="${1}" "${url}" 2> /dev/null
}


extract_usages_from_list() {
	local len=$(echo $1 | jq "length")
	declare -i i
	for ((i = 0; i < $len; i++)); do
		echo "************************"
		local item=$(echo $1 | jq ".[${i}]")
		local trans=$(echo $item | jq -r ".[0]")
		local equivalents=$(echo $item | jq -r ".[1][]" | sed '$!{:a;N;s/\n/\t/;ta}')
		echo -e "\t\t" "$trans" "$equivalents"
	done
}

print_single_usage() {
	local use=$(echo $1 | jq -r ".[0]")
	local list=$(echo $1 | jq ".[2]")
	echo "----------------------------------------------------"
	echo "$use"
	extract_usages_from_list "$list"
}


print_translations() {
	local usage_count=$(echo $1 | jq ".${usage} | length")
	declare -i i
	for ((i = 0; i < $usage_count; i++)); do
		local filter=".${usage}[${i}]"
		u=$(echo $1 | jq --raw-output "$filter")
		print_single_usage "$u"
	done
}


x=$(get_raw_translation "$1")

print_translations "$x"

# echo $x
