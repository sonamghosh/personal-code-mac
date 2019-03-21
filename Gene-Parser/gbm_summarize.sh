#!/bin/bash

# If there is a permission denied msg
# Run sudo chmod 755 gbm_summarize.sh
# Followed by running the script as usual

python3 gbm_summarize.py -g "$@"
