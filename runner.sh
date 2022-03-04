#!/bin/bash

set -o nounset

source_lang=en
to_lang=fa
save=false
POSITIONAL_ARGS=()

parse_args() {
	while [ "$#" -gt 0 ]; do
		case "$1" in
			-sl|--source-language)
				source_lang="$2"
				shift 2
				;;

			-tl|--to-language)
				to_lang="$2"
				shift 2
				;;

			-s|--save)
				save=true
				shift
				;;
		 
			-h|--help)
				echo "Usage: $(basename $0) [-sl|--source-language] [-tl|--to-language] [-s|--save] <word>"
				exit 1
				;;

			*)
				POSITIONAL_ARGS+=("$1")
				shift
			;;

		esac
	done

}


get_raw_translation() {
	url="https://translate.googleapis.com/translate_a/single?client=gtx&ie=UTF-8&oe=UTF-8&dt=bd&dt=ex&dt=ld&dt=md&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=gt&dt=qca&sl=${source_lang}&tl=${to_lang}&hl=en"
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
	local usage_count=$(echo $1 | jq ".[1] | length")
	declare -i i
	for ((i = 0; i < $usage_count; i++)); do
		local filter=".[1][${i}]"
		u=$(echo $1 | jq --raw-output "$filter")
		print_single_usage "$u"
	done
}


parse_args "$@"
set -- "${POSITIONAL_ARGS[@]}"


if [[ "${save}" == true ]]; then
	echo "saving"
	if [ -z "$1" ] || [ -z "$2" ]; then
		echo "provide a word and a meaning"
		exit 1
	else
		query="insert into saved_words (source_language, to_language, word, meaning) VALUES ('${source_lang}', '${to_lang}', '${1}', '${2}');"
		sqlite3 ./test.db "$query"
	fi
else
	if [ ! -z "$1" ]; then
		x=$(get_raw_translation "$1")
		print_translations "$x"
	else
		echo "provide a word"
	fi
fi

