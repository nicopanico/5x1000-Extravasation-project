# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 16:10:43 2025

@author: nicop
"""

import os
import pandas as pd
from datetime import datetime
from config import ROOT_INJECTIONS, ROOT_CONTROLATERALS

## 1__
class DataManager:
    def __init__(self, root_injection=ROOT_INJECTIONS, root_controlateral=ROOT_CONTROLATERALS):
        self.root_injection = root_injection
        self.root_controlateral = root_controlateral

    def get_file_names(self):
        """
        Cerca i file CSV nelle cartelle injection/ e controlaterals/
        che hanno lo stesso 'nome base', dove:
          - Nella cartella injection i file si chiamano ..._inj.csv
          - Nella cartella controlaterals i file si chiamano ..._cont.csv

        Restituisce una lista di questi ID (nome base).
        Esempio: 
          se c'è un file "D223512_2025_03_21_inj.csv" in injection e 
              un file "D223512_2025_03_21_cont.csv" in controlaterals,
          allora genera un id = "D223512_2025_03_21".
        """

        # Trova i file di injection che finiscono con _inj.csv
        inj_files = [f for f in os.listdir(self.root_injection) if f.endswith('_inj.csv')]
        # Trova i file di controlaterals che finiscono con _cont.csv
        con_files = [f for f in os.listdir(self.root_controlateral) if f.endswith('_cont.csv')]

        # Estrai i nomi base togliendo il suffisso '_inj.csv' o '_cont.csv'
        inj_bases = set(f.replace('_inj.csv', '') for f in inj_files)
        con_bases = set(f.replace('_cont.csv', '') for f in con_files)

        # Intersezione dei nomi base
        common_bases = inj_bases.intersection(con_bases)

        return sorted(list(common_bases))
    
    ## 2__
    def load_and_clean_data(self, path, columns_of_interest=None, sep=",", encoding="utf-8"):
            """
            Carica un CSV da `path` e restituisce un DataFrame con:
             - colonna 'Timestamp' convertita in DateTime e impostata come indice (se presente)
             - eventuali altre colonne convertite a float (es. 'Intensità di dose', 'Dose', ecc.)
             - righe con valori NaN eliminate
             - se `columns_of_interest` è un dict, estrai solo quelle colonne e rinominale/convertile.
            
            Esempio di `columns_of_interest`:
                {
                    'time': 'Timestamp',
                    'dose': 'Dose (μSv)',
                    'intensity': 'Intensità di dose (μSv/h)',
                    'count_rate': 'Tasso conteggio (cps)'
                }
    
            Se la colonna esiste, la convertiamo; se non esiste, avvisiamo e ignoriamo.
            """
            try:
                df_raw = pd.read_csv(path, sep=sep, encoding=encoding)
                
                # Se esiste la colonna 'Timestamp', convertiamola e settiamola come indice
                if "Timestamp" in df_raw.columns:
                    df_raw["Timestamp"] = pd.to_datetime(
                        df_raw["Timestamp"],
                        format="%d/%m/%Y %H:%M:%S",  # Adatta al tuo effettivo formato
                        errors="coerce"
                    )
                    df_raw.set_index("Timestamp", drop=True, inplace=True)
                    df_raw.sort_index(ascending=True, inplace=True)
    
                # Se hai passato un dict di colonne di interesse, estrai quelle
                if columns_of_interest:
                    df_clean = pd.DataFrame()
                    for key, col_name in columns_of_interest.items():
                        if col_name in df_raw.columns:
                            if key == "time":
                                # Se 'time' corrisponde a 'Timestamp', in genere è già l'indice
                                # ma potresti volerne tenere una copia come colonna separata
                                df_clean["time"] = df_raw.index  
                            else:
                                # Converte la colonna in float (sostituendo le virgole)
                                df_clean[col_name] = pd.to_numeric(
                                    df_raw[col_name].astype(str).str.replace(",", "."),
                                    errors="coerce"
                                )
                        else:
                            print(f"Attenzione: colonna '{col_name}' non trovata in {path}. Ignorata.")
                    # Rimuoviamo eventuali righe con NaN
                    df_clean.dropna(how="any", inplace=True)
                    return df_clean
                else:
                    # Se non ci sono columns_of_interest, restituiamo l'intero df (pulito un minimo)
                    # Esempio: converti qualche colonna generica se sai che c'è
                    if "Intensità di dose (μSv/h)" in df_raw.columns:
                        df_raw["Intensità di dose (μSv/h)"] = pd.to_numeric(
                            df_raw["Intensità di dose (μSv/h)"].astype(str).str.replace(",", "."),
                            errors="coerce"
                        )
                    df_raw.dropna(how="any", inplace=True)
                    return df_raw
    
            except Exception as e:
                print(f"Errore durante il caricamento di {path}: {e}")
                return pd.DataFrame()
            
    #3__       
    def synchronize_data(self, df_inj: pd.DataFrame, df_con: pd.DataFrame, base_name: str):
        """
        Sincronizza i dati di iniezione (df_inj) e controlaterali (df_con) in base a:
         - differenza di orario di inizio
         - regola: se differenza > 50 min, shift di ~58.4 min al dataset che inizia dopo
         - regola: se nel nome base_name è presente '20_03' o '23_03', aggiungi +3 min al controlaterale
        Ritorna (df_inj_sync, df_con_sync)
        """
        if df_inj.empty or df_con.empty:
            # Se uno dei due DF è vuoto, non facciamo nulla
            return df_inj, df_con
    
        start_inj = df_inj.index[0]
        start_con = df_con.index[0]
        delta = abs(start_inj - start_con)  # differenza di tempo (tipo Timedelta)
        minutes_diff = delta.total_seconds() / 60.0
    
        # Regola 1: se differenza > 50 min => shift -58.4 min al dataset che parte dopo
        if minutes_diff > 50:
            # se injection inizia dopo controlaterale, shift injection
            if start_inj > start_con:
                df_inj.index = df_inj.index - pd.Timedelta(minutes=58.4)
            else:
                # altrimenti, shift controlaterale
                df_con.index = df_con.index - pd.Timedelta(minutes=58.4)
    
        # Regola 2: se nel nome c’è '20_03' o '23_03', shift +3 min al controlaterale
        # (riprendendo la logica del tuo codice "monolitico")
        if "20_03" in base_name or "23_03" in base_name:
            df_con.index = df_con.index + pd.Timedelta(minutes=3)
    
        # Restituiamo i DF con gli indici aggiornati
        return df_inj, df_con