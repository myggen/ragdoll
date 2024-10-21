#!/bin/bash

python3 -m http.server --directory /home/ollama/data/retningslinjer-met/ && sleep 2 &


ollama serve