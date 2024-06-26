#!/bin/bash

# Get the list of installed packages from pip list
packages=$(pip list --format=freeze)

# Uninstall each package
while IFS= read -r line; do
    package_name=$(echo $line | cut -d'=' -f1)
    pip uninstall -y "$package_name"
done <<< "$packages"
