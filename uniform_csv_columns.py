# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 10:12:01 2025

@author: PANICON
"""


import os
import glob
import pandas as pd
import logging

def normalize(s: str) -> str:
    """
    Normalizza una stringa:
      - Rimuove spazi iniziali e finali
      - Converte in minuscolo
      - Sostituisce eventuali spazi multipli con uno singolo
    """
    return " ".join(s.strip().lower().split())

class CSVProcessor:
    """
    Classe per processare un file CSV:
      - Carica il CSV (gestendo in automatico la modalità di lettura e il delimitatore)
      - Rinomina le colonne in base al mapping fornito
      - Salva il file processato nella cartella di output
    """
    def __init__(self, file_path: str, mapping: dict, output_folder: str):
        self.file_path = file_path
        self.mapping = mapping
        self.output_folder = output_folder
        self.df = None

    def load_csv(self):
        """
        Prova a caricare il file CSV con le impostazioni di default (header=0, separatore automatico).
        Se le colonne lette non contengono almeno uno degli indicatori attesi oppure se la prima colonna è 'Filename',
        allora il file probabilmente contiene metadati. In questo caso si riprova a leggere il file usando header=3.
        
        Dopo aver letto con header=3, se il DataFrame ha una sola colonna ed il nome contiene ";" allora si
        ripete la lettura utilizzando sep=";".
        """
        try:
            # Prima lettura: header=0 e separatore automatico
            df_default = pd.read_csv(self.file_path, engine='python', sep=None, on_bad_lines='skip', header=0)
            normalized_columns = [normalize(col) for col in df_default.columns]
            expected_found = any(normalize(variant) in normalized_columns for variant in self.mapping.keys())
            
            if not expected_found or (normalized_columns and normalized_columns[0] == 'filename'):
                logging.info(f"Il file {self.file_path} sembra avere metadati. Riprovo usando header=3.")
                # Proviamo prima con sep='\t'
                df_temp = pd.read_csv(
                    self.file_path,
                    engine='python',
                    sep='\t',
                    on_bad_lines='skip',
                    header=3
                )
                # Se il DataFrame ha una sola colonna e il nome contiene ";" allora il delimitatore è probabilmente ';'
                if len(df_temp.columns) == 1 and ";" in df_temp.columns[0]:
                    logging.info(f"Rilevato delimitatore ';' nel file {self.file_path}. Riprovo con sep=';'.")
                    self.df = pd.read_csv(
                        self.file_path,
                        engine='python',
                        sep=';',
                        on_bad_lines='skip',
                        header=3
                    )
                else:
                    self.df = df_temp
            else:
                self.df = df_default

            logging.info(f"File '{self.file_path}' caricato con colonne: {self.df.columns.tolist()}")
        except Exception as e:
            logging.error(f"Errore loading '{self.file_path}': {e}")
            self.df = None

    def rename_columns(self):
        """
        Rinomina le colonne del DataFrame confrontando (in modo normalizzato) ciascun nome
        con le possibili variazioni presenti nel mapping.
        Se non vengono trovate corrispondenze, logga l'elenco delle colonne lette.
        """
        if self.df is None:
            logging.warning("DataFrame non disponibile, impossibile rinominare le colonne.")
            return

        new_columns = {}
        for col in self.df.columns:
            norm_col = normalize(col)
            for variant, standard in self.mapping.items():
                if norm_col == normalize(variant):
                    new_columns[col] = standard
                    break
        if new_columns:
            logging.info(f"File '{self.file_path}' - colonne rinominate: {new_columns}")
            self.df.rename(columns=new_columns, inplace=True)
        else:
            logging.warning(f"File '{self.file_path}' - Nessuna colonna da rinominare trovata.")
            logging.info(f"Colonne lette: {self.df.columns.tolist()}")

    def save_csv(self):
        """
        Salva il DataFrame processato in un nuovo file CSV.
        Il file viene salvato nella cartella di output, con il nome prefissato da 'processed_'.
        """
        if self.df is None:
            logging.warning("DataFrame non disponibile, niente da salvare per: " + self.file_path)
            return

        base_name = os.path.basename(self.file_path)
        output_path = os.path.join(self.output_folder, f"processed_{base_name}")
        try:
            self.df.to_csv(output_path, index=False)
            logging.info(f"File salvato come '{output_path}'")
        except Exception as e:
            logging.error(f"Errore durante il salvataggio di '{output_path}': {e}")

    def process(self):
        """
        Esegue in sequenza:
          1. Caricamento del CSV
          2. Rinomina delle colonne
          3. Salvataggio del CSV processato
        """
        self.load_csv()
        if self.df is not None:
            self.rename_columns()
            self.save_csv()

def process_directory(input_dir: str, output_dir: str, mapping: dict):
    """
    Processa tutti i file CSV presenti in una determinata cartella.
    Se la cartella di output non esiste, viene creata.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Cartella di output creata: {output_dir}")

    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    if not csv_files:
        logging.warning(f"Nessun file CSV trovato in: {input_dir}")
    for file_path in csv_files:
        processor = CSVProcessor(file_path, mapping, output_dir)
        processor.process()

def main():
    # Configurazione del logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    # Determina il percorso della cartella in cui si trova questo script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Si assume che lo script si trovi in: ...\code\main
    # Quindi la cartella principale del progetto è due livelli sopra:
    root_folder = os.path.abspath(os.path.join(script_dir, "..", ".."))

    # Percorso della cartella contenente i dati da processare
    data_folder = os.path.join(root_folder, "stravaso")
    # Le due sottocartelle con i file CSV
    subfolders = ["injections", "controlaterals"]

    # Cartella di output: verrà creata 'stravaso_processed' nella radice del progetto
    output_root = os.path.join(root_folder, "stravaso_processed")

    # Dizionario di mapping per rinominare le colonne.
    mapping = {
        # Varianti per la colonna timestamp
        "date / time": "timestamp",
        "record time": "timestamp",
        "date/time": "timestamp",  # Variante aggiuntiva
        # Varianti per la colonna dose rate
        "dr_max": "dose_rate",
        "intensità di dose (μsv/h)": "dose_rate",
        "dose rate max value": "dose_rate"
    }

    for subfolder in subfolders:
        input_dir = os.path.join(data_folder, subfolder)
        output_dir = os.path.join(output_root, subfolder)
        logging.info(f"Processando file in '{input_dir}'...")
        process_directory(input_dir, output_dir, mapping)

if __name__ == "__main__":
    main()

