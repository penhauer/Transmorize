#!/bin/bash

from_lang=en
to_lang=fa


main_translation=[0][0][0]
usage=[1]


get_raw_translation() {
	url="https://translate.googleapis.com/translate_a/single?client=gtx&ie=UTF-8&oe=UTF-8&dt=bd&dt=ex&dt=ld&dt=md&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=gt&dt=qca&sl=${from_lang}&tl=${to_lang}&hl=en"
	curl -G --data-urlencode q="${1}" "${url}" 2> /dev/null
}


x=$(get_raw_translation $1)

# echo $x | jq ".$main_translation"


usage_count=$(echo $x | jq ".${usage} | length")

for ((i = 0; i < $usage_count; i++))  do
	echo $i
	z=".${usage}[${i}]"
	echo $z
	echo $x | jq "$z"
done
