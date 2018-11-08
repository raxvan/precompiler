#!/bin/bash

THIS=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
PYTHONPATH="$THIS/:$PYTHONPATH"
export PYTHONPATH

LEXER_TEST_FILE=$THIS/tests/data/cpp_lexer_test.txt
export LEXER_TEST_FILE

echo "============================================================================="
echo "Testing Lexer:"
python3 -m unittest -v $THIS/tests/test_lexer.py

echo "============================================================================="
echo "Running Self Test:"
python3 $THIS/tests/test_precompiler.py $THIS/tests/data/self_test.txt

