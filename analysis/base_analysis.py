# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 16:02:03 2025

@author: PANICON
"""

# analysis/base_analysis.py
from abc import ABC, abstractmethod
import os

class BaseAnalysis(ABC):
    def __init__(self, data_manager, output_dir):
        self.data_manager = data_manager
        self.output_dir = output_dir

    @abstractmethod
    def load_data(self):
        """Carica e pulisce i dati dai file (iniezioni e controlaterali)."""
        pass

    @abstractmethod
    def synchronize_and_align(self, df_inj, df_con, base_name):
        """Sincronizza e allinea i dati (eventualmente con regole specifiche)."""
        pass

    @abstractmethod
    def analyze_peak(self, df_inj, df_con):
        """Esegue l’analisi del picco e calcola le statistiche richieste."""
        pass

    @abstractmethod
    def plot_results(self, base_name, df_inj, df_con, df_inj_filtered, df_con_filtered):
        """Crea e salva i grafici dell’analisi."""
        pass

    def run_analysis(self):
        import os
        import pandas as pd
    
        names = self.data_manager.get_file_names()
        all_stats = []      # Lista di dizionari con statistiche generali
        all_delta = []      # Lista di dizionari con i delta (se calcolati)
        all_ratio_stats = []  # Lista di dizionari con le metriche ratio
        skipped = []        # Pazienti saltati
    
        for base_name in names:
            print(f"Processo: {base_name}")
            inj_path, con_path = self.data_manager.get_paths_for_base(base_name)
            df_inj = self.data_manager.load_and_clean_data(inj_path, self.get_injection_columns())
            df_con = self.data_manager.load_and_clean_data(con_path, self.get_controlateral_columns())
            if df_inj.empty or df_con.empty:
                print(f"Attenzione: {base_name} - uno dei DataFrame è vuoto. Skip.")
                skipped.append(base_name)
                continue
    
            df_inj_sync, df_con_sync = self.synchronize_and_align(df_inj, df_con, base_name)
            if df_inj_sync.empty or df_con_sync.empty:
                print(f"Attenzione: {base_name} - la sincronizzazione ha restituito DataFrame vuoti. Skip.")
                skipped.append(base_name)
                continue
    
            df_inj_filtered, df_con_filtered, stats = self.analyze_peak(df_inj_sync, df_con_sync)
            stats["base_name"] = base_name
            all_stats.append(stats)
    
            # Calcola delta se previsto (se hai già una funzione compute_delta_timepoints)
            from delta_analysis import compute_delta_timepoints
            delta_df = compute_delta_timepoints(
                df_inj_filtered,
                df_con_filtered,
                base_name=base_name,
                column="Intensità di dose (μSv/h)",
                mode="therapy"
            )
            all_delta.append(delta_df.iloc[0].to_dict())
    
            # Recupera le metriche ratio calcolate in analyze_peak tramite compute_therapy_metrics
            all_ratio_stats.append(self.last_ratio_stats)
    
            # Plot dei risultati
            self.plot_results(base_name, df_inj_sync, df_con_sync, df_inj_filtered, df_con_filtered)
    
        # Salvataggio in Excel
        if all_stats:
            stats_df = pd.DataFrame(all_stats)
            delta_df = pd.DataFrame(all_delta)
            ratio_df = pd.DataFrame(all_ratio_stats)
            excel_path = os.path.join(self.output_dir, "risultati_finali.xlsx")
            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                stats_df.to_excel(writer, sheet_name="Stats", index=False, float_format="%.2f")
                if not delta_df.empty:
                    delta_df.to_excel(writer, sheet_name="Delta", index=False, float_format="%.2f")
                if not ratio_df.empty:
                    ratio_df.to_excel(writer, sheet_name="Ratio", index=False, float_format="%.2f")
            print(f"File Excel salvato in: {excel_path}")
    
        if skipped:
            print("I seguenti pazienti sono stati saltati:")
            for name in skipped:
                print(name)


       
        

        