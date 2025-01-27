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
from config import COLUMNS_INJECTION, COLUMNS_CONTROLATERAL

def main():
    data_manager = DataManager()
    names = data_manager.get_file_names()
    print(f"Nomi file in comune trovati: {names}")

    for base_name in names:
        inj_path = os.path.join(data_manager.root_injection, f"{base_name}_inj.csv")
        con_path = os.path.join(data_manager.root_controlateral, f"{base_name}_cont.csv")

        print(f"\nProcesso: {base_name}\n  - Injection: {inj_path}\n  - Controlateral: {con_path}")

        df_inj = data_manager.load_and_clean_data(inj_path, columns_of_interest=COLUMNS_INJECTION)
        df_con = data_manager.load_and_clean_data(con_path, columns_of_interest=COLUMNS_CONTROLATERAL)

        # Verifica se i DataFrame sono vuoti
        if df_inj.empty or df_con.empty:
            print(f"Attenzione: i dati di {base_name} sono vuoti o incompleti. Skip.")
            continue
        # Step 3: sincronizziamo i due DF
        df_inj, df_con = data_manager.synchronize_data(df_inj, df_con, base_name)
        
        
        print(f"df_inj:\n{df_inj.head()}\n")
        print(f"df_con:\n{df_con.head()}\n")

if __name__ == "__main__":
    main()




