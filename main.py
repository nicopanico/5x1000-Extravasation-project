# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 11:54:38 2025

@author: nicop
"""
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 11:54:38 2025

@author: nicop
"""

# main.py

import os
from data_manager import DataManager
from plot_manager import plot_injection_controlateral
from config import COLUMNS_INJECTION, COLUMNS_CONTROLATERAL, PATH_GRAFICI

def main():
    
    # Step 1: Ottenere i nomi base comuni
    data_manager = DataManager()
    names = data_manager.get_file_names()
    print(f"Nomi file in comune trovati: {names}")

    for base_name in names:
        inj_path = os.path.join(data_manager.root_injection, f"{base_name}_inj.csv")
        con_path = os.path.join(data_manager.root_controlateral, f"{base_name}_cont.csv")

        print(f"\nProcesso: {base_name}\n  - Injection: {inj_path}\n  - Controlateral: {con_path}")
        
        # Step 2: Caricamento e pulizia
        df_inj = data_manager.load_and_clean_data(inj_path, columns_of_interest=COLUMNS_INJECTION)
        df_con = data_manager.load_and_clean_data(con_path, columns_of_interest=COLUMNS_CONTROLATERAL)

        # Verifica se i DataFrame sono vuoti
        if df_inj.empty or df_con.empty:
            print(f"Attenzione: i dati di {base_name} sono vuoti o incompleti. Skip.")
            continue
        # Step 3: sincronizziamo i due DF
        df_inj, df_con = data_manager.synchronize_data(df_inj, df_con, base_name)
        
        df_inj = df_inj[~df_inj.index.duplicated(keep='first')]
        df_con = df_con[~df_con.index.duplicated(keep='first')]       
        # Step 4: Allineamento su 15 minuti, freq 1s, riferito a inizio injection
        df_inj, df_con = data_manager.align_with_injection_reference(df_inj, df_con, total_minutes=15)

        print("df_inj (prime 5 righe):")
        print(df_inj.head())
        print("df_con (prime 5 righe):")
        print(df_con.head())
        # Plot
        plot_injection_controlateral(
            base_name=base_name,
            df_inj=df_inj,
            df_con=df_con,
            output_dir=PATH_GRAFICI,
            yscale='log',
            dose_column='Dose (μSv)',
            time_column='time_seconds'
        )
        

if __name__ == "__main__":
    main()




