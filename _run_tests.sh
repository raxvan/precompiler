#!/bin/bash

THIS=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
PYTHONPATH="$THIS/:$PYTHONPATH"
export PYTHONPATH

LEXER_TEST_FILE=$THIS/tests/data/cpp_lexer_test.txt
export LEXER_TEST_FILE

API_TEST_FOLDER=$THIS/tests/data/
export API_TEST_FOLDER


echo "============================================================================="
echo "Testing Lexer:"
cd $THIS/tests/
python3 -m unittest -v test_lexer.py

echo "============================================================================="
echo "Running Self Test:"
ENV_TEST="include_probe.txt"
export ENV_TEST
python3 $THIS/tests/test_precompiler.py $THIS/tests/data/self_test.txt

echo "============================================================================="
echo "Testing Api:"
cd $THIS/tests/
python3 -m unittest -v test_api.py
