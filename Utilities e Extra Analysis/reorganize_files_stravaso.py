# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 12:40:37 2025

@author: panicon
"""

import os
import shutil
from main.config import ROOT_STRAVASO

def reorganize_stravaso(directory_stravaso):
    """
    1) Rinomina i file in 'directory_stravaso':
       - se contengono '_contr', sostituisce con '_cont'
       - altrimenti, se non finisce con '_inj' o '_cont', aggiunge '_inj'
    2) Crea 'injections/' e 'controlaterals/' se non esistono
    3) Sposta i file con '_inj' dentro 'injections/', quelli con '_cont' in 'controlaterals/'
    """
    inj_dir = os.path.join(directory_stravaso, "injections")
    cont_dir = os.path.join(directory_stravaso, "controlaterals")
    os.makedirs(inj_dir, exist_ok=True)
    os.makedirs(cont_dir, exist_ok=True)

    for filename in os.listdir(directory_stravaso):
        old_path = os.path.join(directory_stravaso, filename)
        if os.path.isdir(old_path):
            continue

        basename, ext = os.path.splitext(filename)
        # Esempio: se non è un CSV, saltiamo
        if ext.lower() != ".csv":
            print(f"File '{filename}' non è un CSV (estensione: {ext}). Skip.")
            continue

        # Se qui arrivi, vuol dire che è .csv
        print(f"File '{filename}' è un CSV, posso processarlo...")

        # Rinomina
        new_basename = basename
        if "_contr" in new_basename:
            new_basename = new_basename.replace("_contr", "_cont")
        else:
            if not (new_basename.endswith("_inj") or new_basename.endswith("_cont")):
                new_basename += "_inj"

        new_filename = new_basename + ext

        # Decide in quale sottocartella spostare
        if new_basename.endswith("_inj"):
            final_path = os.path.join(inj_dir, new_filename)
        elif new_basename.endswith("_cont"):
            final_path = os.path.join(cont_dir, new_filename)
        else:
            # fallback, se c'è qualche altro suffisso
            final_path = os.path.join(inj_dir, new_filename)

        print(f"Rinomino e sposto: '{filename}' -> '{final_path}'")
        shutil.move(old_path, final_path)

if __name__ == "__main__":
    # Richiama la funzione puntando a ROOT_STRAVASO
    reorganize_stravaso(ROOT_STRAVASO)
