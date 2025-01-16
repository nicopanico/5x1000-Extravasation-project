# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 16:10:43 2025

@author: nicop
"""

import os
import pandas as pd

def get_file_names_and_activities(root_injections, root_controlaterals):
    """
    Trova i file corrispondenti nelle due directory e ottiene i nomi e le attività.
    """
    names, activities = [], []
    for file_1 in os.listdir(root_injections):
        for file_2 in os.listdir(root_controlaterals):
            file_2 = file_2.split('_contr')[0] + '.csv'
            if file_1 == file_2:
                name, suffix = file_1.split('-')
                activity = int(suffix.split('MBq')[0])
                names.append(name)
                activities.append(activity)
    return names, activities

def load_and_clean_data(path, columns, sep=";", encoding="utf-8"):
    """
    Carica un file CSV e lo pulisce.
    """
    data = pd.read_csv(path, sep=sep, encoding=encoding)
    data['Timestamp'] = pd.to_datetime(data[columns['time']])
    data.set_index('Timestamp', drop=True, inplace=True)
    data = data.sort_index(ascending=True)
    if 'value' in columns:
        data['value'] = pd.to_numeric(data[columns['value']].str.replace(",", "."))
    return data
