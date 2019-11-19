
docker build -t precompiler -f precompiler.dockerfile .
docker run -v %~dp0:/precompiler --rm -it precompiler /bin/bash /precompiler/_run_tests.sh
