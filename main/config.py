
import os

"""
    File di configurazione dei path presenti nella folder principale del progetto
    Questo script permette di non dover inserire i path manualmente all'interno degli script
    permette quindi di lavorare in modo 'relativo'. 
    Requisito fondamentale è che la cartella del progetto sia strutturata correttamente come da README
"""

THIS_FILE = os.path.abspath(__file__)

#   MAIN_DIR = .../code/main
MAIN_DIR = os.path.dirname(THIS_FILE)

#   CODE_DIR = .../code
CODE_DIR = os.path.dirname(MAIN_DIR)

#   PROJECT_DIR = .../5 x 1000 Fuorivena
PROJECT_DIR = os.path.dirname(CODE_DIR)

# Ora possiamo definire i path in base a PROJECT_DIR
ROOT_INJECTIONS = os.path.join(PROJECT_DIR, "injections")
ROOT_CONTROLATERALS = os.path.join(PROJECT_DIR, "controlaterals")
PATH_GRAFICI = os.path.join(PROJECT_DIR, "grafici")

# Se hai "stravaso" come cartella dei file legacy
ROOT_STRAVASO = os.path.join(PROJECT_DIR, "stravaso")

# Se vuoi anche definire "stravaso_plots"
PATH_STRAVASO_PLOTS = os.path.join(ROOT_STRAVASO, "stravaso_plots")


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

