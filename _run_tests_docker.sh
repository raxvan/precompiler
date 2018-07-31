#!/bin/bash

docker build -t precompiler -f precompiler.dockerfile .
THIS=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
docker run -v $THIS/:/precompiler --rm -it precompiler /bin/bash /precompiler/_run_tests.sh