#!/usr/bin/env bash

echo "Building the workflow from the current source code"

rm -f *.alfred3workflow
pip install -r ./src/main/requirements.txt --target ./src/main
rm -rf ./src/main/bin ./src/main/*.dist-info ./src/main/setuptools ./src/main/pkg_resources
python workflow-build.py ./src/main

echo "That's All, Folks !"

