
# config.py
import os

THIS_FILE = os.path.abspath(__file__)
MAIN_DIR = os.path.dirname(THIS_FILE)
PROJECT_DIR = os.path.dirname(MAIN_DIR)

# -----------------------------
# 1) Cartelle per la Terapia
# -----------------------------
THERAPY_DIR = os.path.join(PROJECT_DIR, "Terapia")

ROOT_INJECTIONS_THERAPY = os.path.join(THERAPY_DIR, "injections")
ROOT_CONTROLATERALS_THERAPY = os.path.join(THERAPY_DIR, "controlaterals")
PATH_GRAFICI_THERAPY = os.path.join(THERAPY_DIR, "grafici")

# -----------------------------
# 2) Cartelle per la Diagnostica
# -----------------------------
DIAGNOSTIC_DIR = os.path.join(PROJECT_DIR, "Diagnostica")
STRAVASO_PROCESSED_DIR = os.path.join(DIAGNOSTIC_DIR, "stravaso_processed")

ROOT_INJECTIONS_DIAGNOSTIC = os.path.join(STRAVASO_PROCESSED_DIR, "injections")
ROOT_CONTROLATERALS_DIAGNOSTIC = os.path.join(STRAVASO_PROCESSED_DIR, "controlaterals")
PATH_GRAFICI_DIAGNOSTIC = os.path.join(STRAVASO_PROCESSED_DIR, "grafici")

# Parametri CSV
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
ANALYSIS_MODE = "therapy"  # Cambia in "therapy" se desideri analizzare i dati di Terapia


