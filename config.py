
import os

# Ottieni la directory corrente del file config.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Percorsi relativi alle directory controlaterals e injections
ROOT_CONTROLATERALS = os.path.join(BASE_DIR, "../controlaterals")
ROOT_INJECTIONS = os.path.join(BASE_DIR, "../injections")

# Percorso per salvare i grafici
PATH_GRAFICI = os.path.join(BASE_DIR, "../grafici")

# Parametri CSV
SEPARATOR = ","
ENCODING = "utf-8"

# Colonne di interesse
COLUMNS_INJECTION = {
    'time': 'Timestamp',
    'value': 'Intensità di dose (μSv/h)'
}

COLUMNS_CONTROLATERAL = {
    'time': 'Timestamp',
    'value': 'Intensità di dose (μSv/h)'
}

