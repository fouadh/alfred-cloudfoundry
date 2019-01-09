#!/usr/bin/env bash

echo "Installing the workflow locally from the current source code"

python workflow-install.py -v -s -w '~/Library/Application Support/Alfred 3/Alfred.alfredpreferences/workflows' src/main

echo "That's All, Folks!"
