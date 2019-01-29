#!/usr/bin/env bash

./build.sh
echo "Running the tests..."

cd src/e2e
npm install
npm run cucumber

echo "That's All, Folks!"

