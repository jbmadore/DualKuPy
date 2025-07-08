#!/bin/bash

# Chemin vers le script Python
SCRIPT_PYTHON="/home/nico/DualKuPy/radar_continuous.py"
config_file="/home/nico/DualKuPy/config/config_bonzai_jan_15.json"
# Exécution du script Python
python3 $SCRIPT_PYTHON $config_file

# Mettre l'ordinateur en veille pendant 15 minutes (900 secondes)
rtcwake -m mem -s 900
