#!/usr/bin/env bash

echo "Installing the workflow locally from the current source code"

python workflow-install.py $1 -w '~/Library/Application Support/Alfred 3/Alfred.alfredpreferences/workflows'

echo "That's All, Folks!"
