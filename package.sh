#!/usr/bin/env bash

./build.sh

echo "Build Alfred package..."
rm -f *.alfred3workflow
python workflow-build.py ./src/main

echo "That's All, Folks !"

