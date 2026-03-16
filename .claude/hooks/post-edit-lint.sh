#!/bin/bash
# Post-tool hook: after file edits, check for basic Python syntax errors.
# Only runs on .py files that were just edited.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Only check Python files
if [[ "$FILE_PATH" == *.py ]]; then
  python3 -c "
import py_compile, sys
try:
    py_compile.compile('$FILE_PATH', doraise=True)
except py_compile.PyCompileError as e:
    print(f'SYNTAX ERROR in $FILE_PATH: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1
fi

exit 0
