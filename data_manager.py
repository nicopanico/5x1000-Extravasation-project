# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 16:10:43 2025

@author: nicop
"""

from datetime import timedelta
import os
import pandas as pd
import numpy as np

class DataManager:
    def __init__(self, root_injections, root_controlaterals):
        self.root_injections = root_injections
        self.root_controlaterals = root_controlaterals

    def get_file_names_and_activities(self):
        """
        Trova i file corrispondenti nelle due directory e ottiene i nomi base.
        Restituisce solo i file per cui esistono sia iniezione che controlaterale.
        """
        names = []
        for file_1 in os.listdir(self.root_injections):
            if file_1.endswith('_inj.csv'):  # Cerca solo i file di iniezione
                # Rimuove il suffisso '_inj.csv' per ottenere il nome base
                name = file_1.replace('_inj.csv', '')
                
                # Verifica se esiste il file controlaterale corrispondente
                expected_controlateral = f"{name}_cont.csv"
                if expected_controlateral in os.listdir(self.root_controlaterals):
                    names.append(name)
                else:
                    print(f"File controlaterale mancante per: {name}")
        return names

    def load_and_clean_data(self, path, columns, sep=",", encoding="utf-8"):
        """
        Carica e pulisce i dati da un file CSV.
        :param path: Percorso del file CSV.
        :param columns: Dizionario di colonne da elaborare.
        :param sep: Separatore del file CSV.
        :param encoding: Encoding del file.
        :return: DataFrame processato con le colonne selezionate.
        """
        try:
            # Carica il file CSV
            data = pd.read_csv(path, sep=sep, encoding=encoding)
            
            # Conversione della colonna temporale
            data[columns['time']] = pd.to_datetime(data[columns['time']], format='%d/%m/%Y %H:%M')
            data.set_index(columns['time'], drop=True, inplace=True)
            
            # Conversione delle colonne numeriche
            for key, col in columns.items():
                if key != 'time' and col in data.columns:
                    data[col] = data[col].str.replace(',', '.').astype(float)
            
            return data[list(columns.values())].dropna()
        except Exception as e:
            print(f"Errore durante il caricamento del file {path}: {e}")
            return None

    def synchronize_data(self, df_inj, df_con):
        """
        Sincronizza i dati di iniezione e controlaterali.
        """
        delta = np.abs(df_inj.index[0] - df_con.index[0])
        minutes = delta.total_seconds() / 60
        if minutes > 50:
            if df_inj.index[0] > df_con.index[0]:
                df_inj.index -= timedelta(minutes=58.4)
            else:
                df_con.index -= timedelta(minutes=58.4)
        return df_inj, df_con

