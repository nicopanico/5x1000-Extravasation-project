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
import pandas as pd
from data_manager import DataManager
from peak_analysis import analyze_peak
from plot_manager import plot_injection_controlateral
from config import COLUMNS_INJECTION, COLUMNS_CONTROLATERAL, PATH_GRAFICI
from delta_analysis import compute_delta_timepoints

def main():
    # Step 1
    data_manager = DataManager()
    names = data_manager.get_file_names()
    print(f"Nomi file in comune trovati: {names}")

    all_stats = pd.DataFrame()
    all_delta = pd.DataFrame()

    for base_name in names:
        inj_path = os.path.join(data_manager.root_injection, f"{base_name}_inj.csv")
        con_path = os.path.join(data_manager.root_controlateral, f"{base_name}_cont.csv")

        print(f"\nProcesso: {base_name}\n  - Injection: {inj_path}\n  - Controlateral: {con_path}")

        # Step 2: Caricamento
        df_inj = data_manager.load_and_clean_data(inj_path, columns_of_interest=COLUMNS_INJECTION)
        df_con = data_manager.load_and_clean_data(con_path, columns_of_interest=COLUMNS_CONTROLATERAL)
        if df_inj.empty or df_con.empty:
            print(f"Attenzione: {base_name} - uno dei DF è vuoto. Skip.")
            continue

        # Step 3: sincronizzazione
        df_inj, df_con = data_manager.synchronize_data(df_inj, df_con, base_name)
        df_inj = df_inj[~df_inj.index.duplicated(keep='first')]
        df_con = df_con[~df_con.index.duplicated(keep='first')]

        # Step 4: Allineamento 15 min
        df_inj, df_con = data_manager.align_with_injection_reference(df_inj, df_con, total_minutes=15)

        # Step 5: analisi del picco
        df_inj_filtered, df_con_filtered, stats = analyze_peak(
            df_inj, df_con,
            column_for_peak="Intensità di dose (μSv/h)",
            time_column="time_seconds",
            apply_filter=True,
            filter_sigma=5.0,
            plateau_fraction=0.9
        )
        stats["base_name"] = base_name

        # Aggiungo la riga nel DF globale stats
        row_df = pd.DataFrame([{
            "base_name": stats.get("base_name"),
            "peak_inj_time_s": stats.get("peak_inj_time_s"),
            "peak_inj_value": stats.get("peak_inj_value"),
            "peak_con_time_s": stats.get("peak_con_time_s"),
            "peak_con_value": stats.get("peak_con_value"),
            "mean_inj_filtered": stats.get("mean_inj_filtered"),
            "mean_con_filtered": stats.get("mean_con_filtered"),
            "time_to_plateau_inj": stats.get("time_to_plateau_inj"),
            "time_to_plateau_con": stats.get("time_to_plateau_con")
        }])
        all_stats = pd.concat([all_stats, row_df], ignore_index=True)

        # Step 6: calcolo del delta
        delta_row = compute_delta_timepoints(
            df_inj_filtered,
            df_con_filtered,
            base_name=base_name,
            column="Intensità di dose (μSv/h)",
            time_points=[0,60,120,180,240,300,420,600],
            offset=60
        )
        all_delta = pd.concat([all_delta, delta_row], ignore_index=True)

        # Plot RAW
        plot_injection_controlateral(
            base_name=f"{base_name}_raw",
            df_inj=df_inj,
            df_con=df_con,
            output_dir=PATH_GRAFICI,
            yscale='log',
            dose_column='Intensità di dose (μSv/h)',
            time_column='time_seconds'
        )

        # Plot FILTERED
        plot_injection_controlateral(
            base_name=f"{base_name}_filtered",
            df_inj=df_inj_filtered,
            df_con=df_con_filtered,
            output_dir=PATH_GRAFICI,
            yscale='log',
            dose_column='Intensità di dose (μSv/h)',
            time_column='time_seconds'
        )

    # Fuori dal for: salviamo TUTTI i risultati in unico Excel
    excel_path = os.path.join(PATH_GRAFICI, "risultati_finali.xlsx")
    with pd.ExcelWriter(excel_path) as writer:
        all_stats.to_excel(writer, sheet_name="Stats", index=False, float_format="%.2f")
        all_delta.to_excel(writer, sheet_name="Delta", index=False, float_format="%.2f")

    print(f"File Excel salvato in: {excel_path}")

    # Se non ci serve ritornare i DF, possiamo omettere
    # return df_inj, df_inj_filtered, df_con, df_con_filtered

if __name__ == "__main__":
    main()





