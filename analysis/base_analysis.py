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
    def load_data(self, inj_path, con_path):
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
        import pandas as pd
        from config import ANALYSIS_MODE

        names = self.data_manager.get_file_names()
        all_stats = []
        all_delta = []
        all_ratio_stats = []
        skipped = []

        current_mode = ANALYSIS_MODE.lower()  # "therapy" | "diagnostic" | "inj_only"

        for base_name in names:
            print(f"Processo: {base_name}")
            inj_path, con_path = self.data_manager.get_paths_for_base(base_name)

            # 1) Caricamento dati delegato alla sottoclasse (compatibile con inj_only)
            df_inj, df_con = self.load_data(inj_path, con_path)

            # 2) Check emptiness iniziale (rilassato per inj_only)
            if current_mode == "inj_only":
                if df_inj.empty:
                    print(f"Attenzione: {base_name} - injection vuota. Skip.")
                    skipped.append(base_name)
                    continue
            else:
                if df_inj.empty or df_con.empty:
                    print(f"Attenzione: {base_name} - uno dei DataFrame è vuoto. Skip.")
                    skipped.append(base_name)
                    continue

            # 3) Sincronizzazione/allineamento (rilassato per inj_only)
            df_inj_sync, df_con_sync = self.synchronize_and_align(df_inj, df_con, base_name)
            if current_mode == "inj_only":
                if df_inj_sync.empty:
                    print(f"Attenzione: {base_name} - la sincronizzazione ha restituito injection vuota. Skip.")
                    skipped.append(base_name)
                    continue
            else:
                if df_inj_sync.empty or df_con_sync.empty:
                    print(f"Attenzione: {base_name} - la sincronizzazione ha restituito DataFrame vuoti. Skip.")
                    skipped.append(base_name)
                    continue

            # 4) Analisi picco/metriche (rilassato per inj_only)
            df_inj_filtered, df_con_filtered, stats = self.analyze_peak(df_inj_sync, df_con_sync)
            if current_mode == "inj_only":
                if df_inj_filtered.empty:
                    print(f"{base_name}: dati non validi (inj_only) – skip.")
                    skipped.append(base_name)
                    continue
            else:
                if df_inj_filtered.empty or df_con_filtered.empty:
                    print(f"{base_name}: dati non validi o curva a fondo – skip.")
                    skipped.append(base_name)
                    continue

            stats["base_name"] = base_name
            all_stats.append(stats)

            # 5) Delta timepoints
            from delta_analysis import compute_delta_timepoints
            if current_mode == "therapy":
                delta_df = compute_delta_timepoints(
                    df_inj_filtered,
                    df_con_filtered,
                    base_name=base_name,
                    column="Intensità di dose (μSv/h)",
                    mode="therapy"
                )
                all_delta.append(delta_df.iloc[0].to_dict())
                # ratio only in therapy (se presente)
                if hasattr(self, "last_ratio_stats"):
                    all_ratio_stats.append(self.last_ratio_stats)
            elif current_mode in ("diagnostic", "inj_only"):
                delta_df = compute_delta_timepoints(
                    df_inj_filtered,
                    df_con_filtered,
                    base_name=base_name,
                    column="dose_rate",
                    mode="diagnostic"  # inj_only trattato come diagnostica per durata
                )
                all_delta.append(delta_df.iloc[0].to_dict())

            # 6) Plot risultati
            self.plot_results(base_name, df_inj_sync, df_con_sync, df_inj_filtered, df_con_filtered)

        # 7) Salvataggio in Excel
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
