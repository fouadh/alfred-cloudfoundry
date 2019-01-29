#!/usr/bin/env bash

./build.sh
echo "Running the unit tests..."
cd src/test
pytest -s
echo "That's All, Folks!"

