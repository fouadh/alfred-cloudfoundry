#!/usr/bin/env bash

echo "Building the workflow..."
pip install -r ./src/main/requirements.txt --target ./src/main
rm -rf ./src/main/bin ./src/main/*.dist-info ./src/main/setuptools ./src/main/pkg_resources

echo "That's All, Folks !"

