# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 11:54:38 2025

@author: nicop
"""
from config import (
    ROOT_CONTROLATERALS, ROOT_INJECTIONS, PATH_GRAFICI,
    COLUMNS_INJECTION, COLUMNS_CONTROLATERAL
)
from data_manager import DataManager
import pandas as pd

def main():
    # Inizializza DataManager
    data_manager = DataManager(ROOT_INJECTIONS, ROOT_CONTROLATERALS)

    # Ottenere nomi e attività
    names, activities = data_manager.get_file_names_and_activities()

    # Database finale
    database_inj, database_con = pd.DataFrame(), pd.DataFrame()

    # Elaborazione dei dati
    for name in names:
        inj_path = f"{ROOT_INJECTIONS}/{name}.csv"
        con_path = f"{ROOT_CONTROLATERALS}/{name}_contr.csv"

        # Caricamento dei dati
        df_inj = data_manager.load_and_clean_data(
            inj_path,
            time_column=COLUMNS_INJECTION['time'],
            value_column=COLUMNS_INJECTION['value']
        )
        df_con = data_manager.load_and_clean_data(
            con_path,
            time_column=COLUMNS_CONTROLATERAL['time'],
            value_column=COLUMNS_CONTROLATERAL['value']
        )

        # Sincronizzare i dati
        df_inj, df_con = data_manager.synchronize_data(df_inj, df_con)

        # Aggiungere al database
        database_inj[name] = df_inj[COLUMNS_INJECTION['value']]
        database_con[name] = df_con[COLUMNS_CONTROLATERAL['value']]

    # Esportare i risultati
    database_inj.to_csv(f"{PATH_GRAFICI}/database_inj.csv")
    database_con.to_csv(f"{PATH_GRAFICI}/database_con.csv")

    print(f"Database esportati in {PATH_GRAFICI}")

if __name__ == "__main__":
    main()
