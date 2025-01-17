# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 16:10:43 2025

@author: nicop
"""

import os
import pandas as pd
import numpy as np
from datetime import timedelta


class DataManager:
    def __init__(self, root_injections, root_controlaterals):
        self.root_injections = root_injections
        self.root_controlaterals = root_controlaterals

    def get_file_names_and_activities(self):
        """
        Trova i file corrispondenti nelle due directory e ottiene i nomi e le attività.
        """
        names, activities = [], []
        for file_1 in os.listdir(self.root_injections):
            for file_2 in os.listdir(self.root_controlaterals):
                file_2 = file_2.split('_contr')[0] + '.csv'
                if file_1 == file_2:
                    name, suffix = file_1.split('-')
                    activity = int(suffix.split('MBq')[0])
                    names.append(name)
                    activities.append(activity)
        return names, activities

    def load_and_clean_data(self, path, time_column, value_column, sep=",", encoding="utf-8"):
        """
        Carica e pulisce i dati da un file CSV.
        """
        try:
            data = pd.read_csv(path, sep=sep, encoding=encoding)
            data[time_column] = pd.to_datetime(data[time_column], format='%d/%m/%Y %H:%M')
            data.set_index(time_column, drop=True, inplace=True)
            if value_column in data.columns:
                data[value_column] = data[value_column].str.replace(',', '.').astype(float)
            return data[[value_column]].dropna()
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

