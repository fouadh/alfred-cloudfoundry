#!/usr/bin/env bash

echo "Building the workflow from the current source code"

rm -f *.alfred3workflow
python workflow-build.py ./src/main

echo "That's All, Folks !"

