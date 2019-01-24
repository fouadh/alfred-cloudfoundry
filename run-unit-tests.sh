#!/usr/bin/env bash

echo "Running the unit tests..."
cd src/test
pytest -s
echo "That's All, Folks!"

