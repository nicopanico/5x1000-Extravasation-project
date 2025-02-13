
# config.py
import os

THIS_FILE = os.path.abspath(__file__)
MAIN_DIR = os.path.dirname(THIS_FILE)

# la directory del progetto è il genitore della cartella "code".
PROJECT_DIR = os.path.dirname(MAIN_DIR)

# Percorsi per la terapia
ROOT_INJECTIONS_THERAPY = os.path.join(PROJECT_DIR, "injections")
ROOT_CONTROLATERALS_THERAPY = os.path.join(PROJECT_DIR, "controlaterals")
PATH_GRAFICI_THERAPY = os.path.join(PROJECT_DIR, "grafici")

# Percorsi per la diagnostica
ROOT_INJECTIONS_DIAGNOSTIC = os.path.join(PROJECT_DIR, "stravaso_processed", "injections")
ROOT_CONTROLATERALS_DIAGNOSTIC = os.path.join(PROJECT_DIR, "stravaso_processed", "controlaterals")
PATH_GRAFICI_DIAGNOSTIC = os.path.join(PROJECT_DIR, "stravaso_processed", "grafici")

# Parametri CSV comuni
SEPARATOR = ","
ENCODING = "utf-8"

# Colonne di interesse per la terapia
COLUMNS_INJECTION_THERAPY = {
    'time': 'Timestamp',
    'dose': 'Dose (μSv)',
    'intensity': 'Intensità di dose (μSv/h)',
    'count_rate': 'Tasso conteggio (cps)'
}

COLUMNS_CONTROLATERAL_THERAPY = {
    'time': 'Timestamp',
    'dose': 'Dose (μSv)',
    'intensity': 'Intensità di dose (μSv/h)',
    'count_rate': 'Tasso conteggio (cps)'
}

# Colonne di interesse per la diagnostica  
COLUMNS_INJECTION_DIAGNOSTIC = {
    'time': 'timestamp',
    'dose_rate': 'dose_rate'
}

COLUMNS_CONTROLATERAL_DIAGNOSTIC = {
    'time': 'timestamp',
    'dose_rate': 'dose_rate'
}

# Modalità di analisi: "therapy" o "diagnostic"
ANALYSIS_MODE = "therapy"  # Cambia in "diagnostic" se vuoi analizzare dati diagnostici



