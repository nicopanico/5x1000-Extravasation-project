# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 09:26:59 2025

@author: PANICON
"""

# analysis/diagnostic_analysis.py
from analysis.base_analysis import BaseAnalysis
from peak_analysis import analyze_peak  # Se possibile, puoi riutilizzare la funzione oppure crearne una versione specifica
from delta_analysis import compute_delta_timepoints
from plot_manager import plot_injection_controlateral

class DiagnosticAnalysis(BaseAnalysis):
    def get_injection_columns(self):
        from config import COLUMNS_INJECTION_DIAGNOSTIC
        return COLUMNS_INJECTION_DIAGNOSTIC

    def get_controlateral_columns(self):
        from config import COLUMNS_CONTROLATERAL_DIAGNOSTIC
        return COLUMNS_CONTROLATERAL_DIAGNOSTIC

    def synchronize_and_align(self, df_inj, df_con, base_name):
        # Riutilizziamo le regole di sincronizzazione già presenti nel DataManager
        df_inj_sync, df_con_sync = self.data_manager.synchronize_data(df_inj, df_con, base_name)
        # Per l'allineamento usiamo lo stesso metodo (ad esempio 15 minuti di finestra)
        df_inj_aligned, df_con_aligned = self.data_manager.align_with_injection_reference(df_inj_sync, df_con_sync, total_minutes=15)
        return df_inj_aligned, df_con_aligned

    def analyze_peak(self, df_inj, df_con):
        """
        Per la diagnostica, il file ha le colonne "Timestamp" e "dose_rate".
        Usiamo la funzione analyze_peak, adattando i parametri:
          - column_for_peak: 'dose_rate'
          - time_column: 'time_seconds'
          - possiamo usare un filtro con sigma minore (ad esempio 3.0)
          - plateau_fraction leggermente diversa (ad esempio 0.85)
        Inoltre, aggiungiamo le metriche extra:
          - delta_dose: differenza fra il picco e la media (plateau)
          - ratio_dose: (picco - media) / picco
        """
        df_inj_filtered, df_con_filtered, stats = analyze_peak(
            df_inj, df_con,
            column_for_peak="dose_rate",
            time_column="time_seconds",
            apply_filter=True,
            filter_sigma=3.0,   # Parametro adattato per diagnostica
            plateau_fraction=0.85
        )

        # Aggiungiamo le metriche extra
        # Assumiamo che stats contenga "peak_inj_value" e "mean_inj_filtered"
        peak_value = stats.get("peak_inj_value")
        mean_value = stats.get("mean_inj_filtered")
        if peak_value is not None and mean_value is not None:
            delta_dose = peak_value - mean_value
            ratio_dose = (peak_value - mean_value) / peak_value if peak_value != 0 else None
        else:
            delta_dose = None
            ratio_dose = None

        stats["delta_dose"] = delta_dose
        stats["ratio_dose"] = ratio_dose

        # Eventuali ulteriori metriche possono essere aggiunte qui

        return df_inj_filtered, df_con_filtered, stats

    def plot_results(self, base_name, df_inj, df_con, df_inj_filtered, df_con_filtered):
        from config import PATH_GRAFICI_DIAGNOSTIC
        # Plot dei dati originali
        plot_injection_controlateral(
            base_name=base_name,
            df_inj=df_inj,
            df_con=df_con,
            output_dir=PATH_GRAFICI_DIAGNOSTIC,
            yscale='log',
            dose_column='dose_rate',      # Usato per diagnostica
            time_column='time_seconds'
        )
        # Plot dei dati filtrati
        plot_injection_controlateral(
            base_name=f"{base_name}_filtered",
            df_inj=df_inj_filtered,
            df_con=df_con_filtered,
            output_dir=PATH_GRAFICI_DIAGNOSTIC,
            yscale='log',
            dose_column='dose_rate',
            time_column='time_seconds'
        )

