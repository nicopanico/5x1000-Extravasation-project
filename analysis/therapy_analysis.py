# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 16:04:22 2025

@author: PANICON
"""
# analysis/therapy_analysis.py
from analysis.base_analysis import BaseAnalysis
from peak_analysis import analyze_peak
from plot_manager import plot_injection_controlateral
import numpy as np
import pandas as pd



class TherapyAnalysis(BaseAnalysis):
    def get_injection_columns(self):
        from config import COLUMNS_INJECTION_THERAPY
        return COLUMNS_INJECTION_THERAPY

    def get_controlateral_columns(self):
        from config import COLUMNS_CONTROLATERAL_THERAPY
        return COLUMNS_CONTROLATERAL_THERAPY
    
    def load_data(self, inj_path, con_path):
        df_inj = self.data_manager.load_and_clean_data(inj_path, self.get_injection_columns())
        df_con = self.data_manager.load_and_clean_data(con_path, self.get_controlateral_columns())
        return df_inj, df_con
    
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
        # Calcola metriche aggiuntive per la terapia
        stats, ratio_stats = self.compute_therapy_metrics(
            df_inj_filtered,
            df_con_filtered,
            stats,
            time_column="time_seconds",
            dose_column="Intensità di dose (μSv/h)"
        )
        # Salva anche le metriche ratio in un attributo se vuoi usarle per il plotting
        self.last_ratio_stats = ratio_stats
        self.last_stats = stats  # se vuoi salvare anche gli altri stats
        return df_inj_filtered, df_con_filtered, stats

    def plot_results(self, base_name, df_inj, df_con, df_inj_filtered, df_con_filtered):
        from config import PATH_GRAFICI_THERAPY    
        
        plot_injection_controlateral(
            base_name=f"{base_name}_filtered",
            df_inj=df_inj_filtered,
            df_con=df_con_filtered,
            output_dir=PATH_GRAFICI_THERAPY,
            yscale='log',
            dose_column="Intensità di dose (μSv/h)",
            time_column="time_seconds",
            stats=self.last_stats,       # Statistiche generali
            ratio_stats=self.last_ratio_stats  # Statistiche ratio
        )
        
    def compute_therapy_metrics(self, df_inj, df_con, stats, time_column="time_seconds", dose_column="Intensità di dose (μSv/h)"):
        if df_inj.empty or df_con.empty:
            return stats, {}
        
        # --- Calcolo delle metriche base ---
        # 1) Tempo al 90% del plateau per injection
        last_30_inj = df_inj.iloc[-30:] if len(df_inj) >= 30 else df_inj
        plateau_inj = last_30_inj[dose_column].mean()
        threshold_inj = 0.9 * plateau_inj
        time_90_inj = None
        mask_inj = df_inj[dose_column] >= threshold_inj
        if mask_inj.any():
            idx_first = mask_inj.idxmax()
            time_90_inj = df_inj.loc[idx_first, time_column]
        stats["time_to_90pct_inj"] = time_90_inj
    
        # 2) Tempo al 90% del plateau per controlateral
        last_30_con = df_con.iloc[-30:] if len(df_con) >= 30 else df_con
        plateau_con = last_30_con[dose_column].mean()
        threshold_con = 0.9 * plateau_con
        time_90_con = None
        mask_con = df_con[dose_column] >= threshold_con
        if mask_con.any():
            idx_first_con = mask_con.idxmax()
            time_90_con = df_con.loc[idx_first_con, time_column]
        stats["time_to_90pct_con"] = time_90_con
    
        # 3) AUC-delta
        diff_series = df_inj[dose_column] - df_con[dose_column]
        time_array = df_inj[time_column].values
        auc_delta = np.trapz(diff_series, x=time_array)
        stats["AUC_delta"] = auc_delta
    
        # 4) Slope iniziale injection (0-120s)
        t_max_slope = 120
        df_inj_slope = df_inj[df_inj[time_column] <= t_max_slope]
        if len(df_inj_slope) >= 2:
            dose_0 = df_inj_slope.iloc[0][dose_column]
            time_0 = df_inj_slope.iloc[0][time_column]
            dose_end = df_inj_slope.iloc[-1][dose_column]
            time_end = df_inj_slope.iloc[-1][time_column]
            slope_inj = (dose_end - dose_0) / (time_end - time_0) if (time_end != time_0) else None
        else:
            slope_inj = None
        stats["slope_inj_0_120s"] = slope_inj
    
        # --- Calcolo delle metriche ratio (da salvare separatamente) ---
        # Crea un dizionario per le metriche ratio.
        ratio_stats = {}
        
        # Calcola il rapporto injection/controlaterale
        ratio_series = df_inj[dose_column] / df_con[dose_column].replace(0, np.nan)
        
        # Calcola una serie di ratio ad intervalli:
        max_time = df_inj[time_column].max()
        max_interval = 15 * 60  # 15 minuti in secondi
        end_time = int(min(max_interval, max_time))
        intervals = list(range(60, end_time + 1, 60))
        for t in intervals:
            # Trova l'indice in cui il valore in time_seconds è più vicino a t
            idx = (df_inj[time_column] - t).abs().idxmin()
            val_ratio = ratio_series.loc[idx] if idx in ratio_series.index else np.nan
            ratio_stats[f"ratio_{t}s"] = val_ratio
    
        # Calcola la media dei ratio ad intervalli
        ratio_values = [v for v in ratio_stats.values() if pd.notna(v)]
        ratio_stats["ratio_intervals_mean"] = np.nanmean(ratio_values) if ratio_values else np.nan
        # Calcola il massimo ratio
        ratio_stats["ratio_max"] = ratio_series.max(skipna=True)
        # Calcola la media globale del rapporto
        ratio_stats["ratio_mean"] = ratio_series.mean(skipna=True)
    
        return stats, ratio_stats
