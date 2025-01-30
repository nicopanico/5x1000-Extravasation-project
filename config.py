
import os

# Ottieni la directory base del progetto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Percorsi relativi alle directory controlaterals e injections
ROOT_CONTROLATERALS = os.path.join(BASE_DIR, "controlaterals")
ROOT_INJECTIONS = os.path.join(BASE_DIR, "injections")

# Percorso per i grafici
PATH_GRAFICI = os.path.join(BASE_DIR, "grafici")

# Parametri CSV
SEPARATOR = ","
ENCODING = "utf-8"

# Colonne di interesse per le iniezioni
COLUMNS_INJECTION = {
    'time': 'Timestamp',
    'dose': 'Dose (μSv)',
    'intensity': 'Intensità di dose (μSv/h)',
    'count_rate': 'Tasso conteggio (cps)'
}

# Colonne di interesse per i controlaterali
COLUMNS_CONTROLATERAL = {
    'time': 'Timestamp',
    'dose': 'Dose (μSv)',
    'intensity': 'Intensità di dose (μSv/h)',
    'count_rate': 'Tasso conteggio (cps)'
}

