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

    # Ottenere i nomi dei file da processare
    names = data_manager.get_file_names_and_activities()
    print(f"Nomi rilevati: {names}")

    # Database finale
    database_inj, database_con = pd.DataFrame(), pd.DataFrame()

    # Elaborazione dei dati
    for name in names:
        # Costruzione dei percorsi relativi ai file
        inj_path = f"{ROOT_INJECTIONS}/{name}_inj.csv"
        con_path = f"{ROOT_CONTROLATERALS}/{name}_cont.csv"

        print(f"Processing file: {name}")
        print(f"Injection path: {inj_path}")
        print(f"Controlateral path: {con_path}")

        # Caricamento dei dati
        df_inj = data_manager.load_and_clean_data(
            inj_path,
            columns=COLUMNS_INJECTION
        )
        df_con = data_manager.load_and_clean_data(
            con_path,
            columns=COLUMNS_CONTROLATERAL
        )

        # Sincronizzazione
        df_inj, df_con = data_manager.synchronize_data(df_inj, df_con)

        # Aggiungere i dati al database
        database_inj[name] = df_inj[COLUMNS_INJECTION['intensity']]
        database_con[name] = df_con[COLUMNS_CONTROLATERAL['intensity']]

        # Esportare i risultati
        output_inj_path = f"{PATH_GRAFICI}/database_inj_{name}.csv"
        output_con_path = f"{PATH_GRAFICI}/database_con_{name}.csv"

        database_inj.to_csv(output_inj_path)
        database_con.to_csv(output_con_path)

        print(f"Database esportati in:\n{output_inj_path}\n{output_con_path}")

if __name__ == "__main__":
    main()
