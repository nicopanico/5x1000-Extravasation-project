
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
    "time": [],
    "dose_rate": []
}

COLUMNS_INJECTION_DIAGNOSTIC["time"] = list({
    *COLUMNS_INJECTION_DIAGNOSTIC.get("time", []),
    "timestamp", "time", "date time", "date/time", "datetime", "data/ora", "record time"
})

COLUMNS_INJECTION_DIAGNOSTIC["dose_rate"] = list({
    *COLUMNS_INJECTION_DIAGNOSTIC.get("dose_rate", []),
    "dose_rate", "dose rate",
    "intensità di dose (usv/h)", "intensita di dose (usv/h)",
    "intensità di dose (uSv/h)".lower(),   # se vuoi coprire casi strani
    
})
COLUMNS_CONTROLATERAL_DIAGNOSTIC = {
    "time"      : ["timestamp", "Timestamp"],
    "dose_rate" : ["dose_rate", "Dose Rate", "Intensità di dose (μSv/h)"]
}

# Modalità di analisi: "therapy" o "diagnostic"
ANALYSIS_MODE = "inj_only"  # Cambia in "therapy" se desideri analizzare i dati di Terapia
# ANALYSIS_MODE = "therapy"
# ANALYSIS_MODE = "diagnostic"
# ANALYSIS_MODE = "inj_only"  # Solo dosimetro injection, senza controlaterale

# --- Plot inj_only ---
# Se None: autoscale log. Se tuple: limiti fissi condivisi per il grafico assoluto.
INJ_ONLY_COMMON_YLIM = (10, 5000)        # es. (10, 1000) se vuoi fissare la scala
INJ_ONLY_PLOT_NORMALIZED = True    # salva anche il grafico normalizzato
INJ_ONLY_SUBDIR_PLOT = "plot"
INJ_ONLY_SUBDIR_NORM = "normalized_plot"
