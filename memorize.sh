SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PYTHON_INTERPRETER="${SCRIPT_DIR}/venv/bin/python3"
MEMORIZE_PATH="${SCRIPT_DIR}/memorize.py"
exec "${PYTHON_INTERPRETER}" "${MEMORIZE_PATH}" "$@"
