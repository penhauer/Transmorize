#!/bin/bash

from_lang=en
to_lang=fa


main_translation=[0][0][0]
usage=[1]


get_raw_translation() {
	url="https://translate.googleapis.com/translate_a/single?client=gtx&ie=UTF-8&oe=UTF-8&dt=bd&dt=ex&dt=ld&dt=md&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=gt&dt=qca&sl=${from_lang}&tl=${to_lang}&hl=en"
	curl -G --data-urlencode q="${1}" "${url}" 2> /dev/null
}


print_single_usage() {
	local len=$(echo $1 | jq "length")
	for ((i = 0; i < $len; i++)); do
		echo "-------------------------------------------------------------"
		echo $1 | jq ".[${i}]"
		echo
		echo
		echo
	done
}


print_translations() {
	local usage_count=$(echo $1 | jq ".${usage} | length")
	for ((i = 0; i < $usage_count; i++)); do
		local filter=".${usage}[${i}][2]"
		u=$(echo $1 | jq --raw-output "$filter")
		print_single_usage "$u"
	done
}


x=$(get_raw_translation "$1")

print_translations "$x"

echo $x
