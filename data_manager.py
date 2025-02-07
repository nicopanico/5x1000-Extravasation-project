# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 16:10:43 2025

@author: nicop
"""

import os
import pandas as pd
from datetime import datetime


## 1__
class DataManager:
    def __init__(self, root_injection, root_controlateral):
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
        try:
            # Legge il CSV usando decimal="," per interpretare correttamente i numeri
            df_raw = pd.read_csv(path, sep=sep, encoding=encoding, decimal=",")
            # Rimuove spazi extra nei nomi delle colonne
            df_raw.columns = df_raw.columns.str.strip()
            
            # Se l'analisi è in modalità diagnostica, trasforma i nomi delle colonne in minuscolo
            from config import ANALYSIS_MODE
            if ANALYSIS_MODE.lower() == "diagnostic":
                df_raw.columns = df_raw.columns.str.lower()
            else:
                df_raw.columns = df_raw.columns.str.strip()
            
            # Se ci sono colonne duplicate, mantieni la prima
            if df_raw.columns.duplicated().any():
                df_raw = df_raw.loc[:, ~df_raw.columns.duplicated(keep='first')]
            
            # Gestione della colonna del tempo
            if columns_of_interest and "time" in columns_of_interest:
                time_col = columns_of_interest["time"]
                if time_col not in df_raw.columns:
                    # Se non trova la colonna, prova una re-lettura con header=None e nomi predefiniti
                    print(f"Attenzione: la colonna del tempo '{time_col}' non è presente in {path}. Provo a re-lettura con header=None.")
                    default_names = [
                        "timestamp", "###", "Type", "Status", "Alarm status", "C1_Max", "C1_Mean",
                        "dose_rate", "DR_Mean", "Neutron_Max", "Neutron_Mean", "Msd time",
                        "Spectrum##", "Temperature", "OperationTime", "Alarm threshold 1",
                        "Alarm threshold 2", "Alarm threshold 3", "Alarm threshold 4",
                        "Alarm threshold 5", "Alarm threshold 6", "Unnamed: 21"
                    ]
                    df_raw = pd.read_csv(path, sep=sep, encoding=encoding, header=None, names=default_names, decimal=",")
                    df_raw.columns = df_raw.columns.str.strip()
                    if df_raw.columns.duplicated().any():
                        df_raw = df_raw.loc[:, ~df_raw.columns.duplicated(keep='first')]
                    if time_col not in df_raw.columns:
                        print(f"Attenzione: la colonna del tempo '{time_col}' non è presente nemmeno dopo la re-lettura di {path}. Skip questo file.")
                        return pd.DataFrame()
                # Conversione della colonna del tempo in datetime
                df_raw[time_col] = pd.to_datetime(df_raw[time_col],
                                                  format="%d/%m/%Y %H:%M:%S",
                                                  dayfirst=True,
                                                  errors="coerce")
                # Imposta la colonna del tempo come indice **ma la mantiene anche come colonna**
                df_raw.set_index(time_col, drop=False, inplace=True)
                df_raw.sort_index(ascending=True, inplace=True)
                # Rimuove eventuali duplicati nell'indice
                df_raw = df_raw[~df_raw.index.duplicated(keep='first')]
            else:
                if "Timestamp" in df_raw.columns:
                    df_raw["Timestamp"] = pd.to_datetime(df_raw["Timestamp"],
                                                         format="%d/%m/%Y %H:%M:%S",
                                                         dayfirst=True,
                                                         errors="coerce")
                    df_raw.set_index("Timestamp", drop=False, inplace=True)
                    df_raw.sort_index(ascending=True, inplace=True)
                    df_raw = df_raw[~df_raw.index.duplicated(keep='first')]
            
            # Debug: stampa il DataFrame dopo la conversione dell'indice
            # print("DataFrame dopo la conversione dell'indice:")
            # if "dose_rate" in df_raw.columns:
            #     print(df_raw["dose_rate"].head())
            # print("Tipi di dato:")
            # print(df_raw.dtypes)
            
            # Estrazione delle colonne di interesse
            if columns_of_interest:
                # Costruisci un DataFrame che contenga le colonne desiderate.
                # In questo esempio, vogliamo avere "time" (ottenuto dal valore dell'indice, ora presente come colonna)
                # e "dose_rate".
                df_clean = df_raw.copy()[[columns_of_interest["time"], columns_of_interest.get("dose_rate", "dose_rate")]]
                # Rinomina la colonna del tempo in "time" (se non lo è già)
                df_clean.rename(columns={columns_of_interest["time"]: "time"}, inplace=True)
                # Se vuoi assicurarti che la colonna "time" contenga i valori dal DataFrame (non l'indice)
                # Puoi anche usare: df_clean["time"] = df_clean["time"].values
                # Applica dropna solo su "dose_rate" (o su quelle colonne essenziali)
                df_clean.dropna(subset=["dose_rate"], inplace=True)
                return df_clean
            else:
                df_raw.dropna(how="any", inplace=True)
                return df_raw
    
        except Exception as e:
            print(f"Errore durante il caricamento di {path}: {e}")
            return pd.DataFrame()

        
    #3__       
    def synchronize_data(self, df_inj: pd.DataFrame, df_con: pd.DataFrame, base_name: str):
        if df_inj.empty or df_con.empty:
            return df_inj, df_con
    
        # Estrai il primo timestamp da ciascun DataFrame
        start_inj = df_inj.index[0]
        start_con = df_con.index[0]
    
        # Se uno dei timestamp è NaT, stampare un messaggio e restituire DataFrame vuoti per segnalare che questo file va saltato
        if pd.isna(start_inj) or pd.isna(start_con):
            print(f"Attenzione: per il paziente {base_name} uno dei timestamp iniziali è NaT. Skip questo file.")
            return pd.DataFrame(), pd.DataFrame()
    
        # Calcola la differenza di tempo e procedi normalmente
        delta = abs(start_inj - start_con)
        minutes_diff = delta.total_seconds() / 60.0
    
        if minutes_diff > 50:
            if start_inj > start_con:
                df_inj.index = df_inj.index - pd.Timedelta(minutes=58.4)
            else:
                df_con.index = df_con.index - pd.Timedelta(minutes=58.4)
    
        if "20_03" in base_name or "23_03" in base_name:
            df_con.index = df_con.index + pd.Timedelta(minutes=3)
    
        return df_inj, df_con

    
    # 4_
    def get_paths_for_base(self, base_name):
        """
        Dato un nome base, restituisce i percorsi completi dei file di injection e controlateral.
        Si assume che:
          - Il file di injection si chiami "{base_name}_inj.csv"
          - Il file di controlateral si chiami "{base_name}_cont.csv"
        """
        inj_path = os.path.join(self.root_injection, f"{base_name}_inj.csv")
        con_path = os.path.join(self.root_controlateral, f"{base_name}_cont.csv")
        return inj_path, con_path
    
    def align_with_injection_reference(self, df_inj, df_con, total_minutes=15):
        if df_inj.empty or df_con.empty:
            return df_inj, df_con
    
        # Rimuovi duplicati nell'indice, se presenti
        df_inj = df_inj[~df_inj.index.duplicated(keep='first')]
        df_con = df_con[~df_con.index.duplicated(keep='first')]
    
        # Se esiste una colonna duplicata del tempo (come "timestamp" o "Timestamp"), eliminala.
        for col in ["timestamp", "Timestamp"]:
            if col in df_inj.columns:
                df_inj = df_inj.drop(columns=[col])
            if col in df_con.columns:
                df_con = df_con.drop(columns=[col])
    
        # 1) Istante di inizio: usa il primo timestamp dell'injection
        inj_start_time = df_inj.index[0]
        # 2) Calcola l'intervallo totale
        inj_end_time = inj_start_time + pd.Timedelta(minutes=total_minutes)
        # 3) Crea un nuovo DatetimeIndex regolare con frequenza di 1 secondo
        time_range = pd.date_range(start=inj_start_time, end=inj_end_time, freq='1s')
    
        # 4) Taglia i DataFrame per avere dati solo nell'intervallo [inj_start_time, inj_end_time]
        df_inj_cut = df_inj.loc[(df_inj.index >= inj_start_time) & (df_inj.index <= inj_end_time)].copy()
        df_con_cut = df_con.loc[(df_con.index >= inj_start_time) & (df_con.index <= inj_end_time)].copy()
    
        # 5) Reindexa i DataFrame sul nuovo time_range e interpola con metodo lineare
        df_inj_aligned = df_inj_cut.reindex(time_range).interpolate(method='linear')
        df_con_aligned = df_con_cut.reindex(time_range).interpolate(method='linear')
    
        # 6) Aggiungi colonne per il timestamp originale e per il tempo in secondi dall'inizio
        df_inj_aligned['original_timestamp'] = df_inj_aligned.index
        df_inj_aligned['time_seconds'] = (df_inj_aligned.index - inj_start_time).total_seconds()
        df_con_aligned['original_timestamp'] = df_con_aligned.index
        df_con_aligned['time_seconds'] = (df_con_aligned.index - inj_start_time).total_seconds()
    
        # 7) Se vuoi avere il timestamp come colonna, aggiungila (oppure rinominala in "time")
        df_inj_aligned['time'] = df_inj_aligned.index
        df_con_aligned['time'] = df_con_aligned.index
    
        # 8) Se desideri resettare l'indice per avere un DataFrame a indice numerico (opzionale)
        df_inj_aligned.reset_index(drop=True, inplace=True)
        df_con_aligned.reset_index(drop=True, inplace=True)
    
        return df_inj_aligned, df_con_aligned
    
    
