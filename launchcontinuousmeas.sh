#!/bin/bash

# Chemin vers le script Python
SCRIPT_PYTHON="./radar_continuous.py"

# Exécution du script Python
python3 $SCRIPT_PYTHON

# Mettre l'ordinateur en veille pendant 15 minutes (900 secondes)
rtcwake -m mem -s 900
