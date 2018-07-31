#!/bin/bash

THIS=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
PYTHONPATH="$THIS/:$PYTHONPATH"
export PYTHONPATH

TEST_FILE=$THIS/tests/data/cpp_lexer_test.txt
export TEST_FILE
python3 -m unittest -v $THIS/tests/test_lexer.py
#python3 $THIS/tests/test_precompiler.py $THIS/tests/data/base.txt
#python3 $THIS/tests/test_precompiler.py $THIS/tests/data/includes.txt

