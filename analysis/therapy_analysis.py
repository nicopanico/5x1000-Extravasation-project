# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 16:04:22 2025

@author: PANICON
"""
# analysis/therapy_analysis.py
from analysis.base_analysis import BaseAnalysis
from peak_analysis import analyze_peak
from delta_analysis import compute_delta_timepoints
from plot_manager import plot_injection_controlateral

class TherapyAnalysis(BaseAnalysis):
    def get_injection_columns(self):
        from config import COLUMNS_INJECTION_THERAPY
        return COLUMNS_INJECTION_THERAPY

    def get_controlateral_columns(self):
        from config import COLUMNS_CONTROLATERAL_THERAPY
        return COLUMNS_CONTROLATERAL_THERAPY

    def synchronize_and_align(self, df_inj, df_con, base_name):
        df_inj_sync, df_con_sync = self.data_manager.synchronize_data(df_inj, df_con, base_name)
        df_inj_aligned, df_con_aligned = self.data_manager.align_with_injection_reference(df_inj_sync, df_con_sync, total_minutes=15)
        return df_inj_aligned, df_con_aligned

    def analyze_peak(self, df_inj, df_con):
        df_inj_filtered, df_con_filtered, stats = analyze_peak(
            df_inj, df_con,
            column_for_peak="Intensità di dose (μSv/h)",
            time_column="time_seconds",
            apply_filter=True,
            filter_sigma=5.0,
            plateau_fraction=0.9
        )
        # (Eventuale chiamata a compute_additional_metrics se desiderato per terapia)
        return df_inj_filtered, df_con_filtered, stats

    def plot_results(self, base_name, df_inj, df_con, df_inj_filtered, df_con_filtered):
        from config import PATH_GRAFICI_THERAPY
        plot_injection_controlateral(
            base_name=base_name,
            df_inj=df_inj,
            df_con=df_con,
            output_dir=PATH_GRAFICI_THERAPY,
            yscale='log',
            dose_column='Intensità di dose (μSv/h)',
            time_column='time_seconds'
        )
        plot_injection_controlateral(
            base_name=f"{base_name}_filtered",
            df_inj=df_inj_filtered,
            df_con=df_con_filtered,
            output_dir=PATH_GRAFICI_THERAPY,
            yscale='log',
            dose_column='Intensità di dose (μSv/h)',
            time_column='time_seconds'
        )
