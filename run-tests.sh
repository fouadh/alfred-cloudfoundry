#!/usr/bin/env bash

echo "Running the tests..."

cd src/test
npm install
npm run cucumber

echo "That's All, Folks!"

