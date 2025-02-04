# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 10:58:00 2025

@author: nicop
"""

# peak_analysis.py

import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d

def find_peak(df_inj, column_for_peak="Dose (μSv)", time_column="time_seconds"):
    """
    Trova l'indice del picco nella colonna `column_for_peak` di df_inj 
    Ritorna (peak_idx, peak_time_s, peak_value).
    """
    if df_inj.empty:
        return None, None, None

    peak_idx = df_inj[column_for_peak].idxmax()  # indice del max
    peak_value = df_inj.loc[peak_idx, column_for_peak]
    peak_time_s = df_inj.loc[peak_idx, time_column]  # tempo in secondi corrispondente

    return peak_idx, peak_time_s, peak_value

def slice_data(df, time_column="time_seconds", start_time=0, end_time=600):
    """
    Ritorna un subset di df dove df[time_column] è in [start_time, end_time].
    """
    if df.empty:
        return df
    mask = (df[time_column] >= start_time) & (df[time_column] <= end_time)
    return df.loc[mask].copy()

def apply_gaussian_filter_to_column(df, column, sigma=5):
    """
    Applica un filtro gaussiano 1D sulla colonna data. 
    Sovrascrive i valori in df[column]. 
    Ritorna df modificato.
    """
    if df.empty:
        return df
    df[column] = gaussian_filter1d(df[column], sigma=sigma)
    return df

def compute_stats(df_inj, df_con, column_for_peak="Dose (μSv)"):
    """
    Esempio di funzioni di calcolo statistiche sull'intervallo (df_inj, df_con).
    Ritorna un dict con 'mean_inj', 'mean_con', ecc.
    """
    stats = {}
    if not df_inj.empty:
        stats["mean_inj"] = df_inj[column_for_peak].mean()
        stats["max_inj"] = df_inj[column_for_peak].max()
    else:
        stats["mean_inj"] = np.nan
        stats["max_inj"] = np.nan

    if not df_con.empty:
        stats["mean_con"] = df_con[column_for_peak].mean()
        stats["max_con"] = df_con[column_for_peak].max()
    else:
        stats["mean_con"] = np.nan
        stats["max_con"] = np.nan

    return stats

def analyze_peak(
    df_inj: pd.DataFrame,
    df_con: pd.DataFrame,
    column_for_peak: str = "Intensità di dose (μSv/h)",
    time_column: str = "time_seconds",
    apply_filter: bool = False,
    filter_sigma: float = 5.0,
    plateau_fraction: float = 0.9
):
    """
    1) Applica (opzionale) un filtro gaussiano a injection e controlaterale (sull'intero DF).
    2) Trova il picco su injection filtrata e su controlaterale filtrata (tempo e valore).
    3) Calcola la media su injection e controlaterale (filtrate).
    4) Calcola tempo al plateau (plateau_fraction * picco) per injection e controlaterale.

    Ritorna:
      (df_inj_filtered, df_con_filtered, stats_dict)

    stats_dict contiene campi come:
      peak_inj_time_s, peak_inj_value,
      peak_con_time_s, peak_con_value,
      mean_inj_filtered, mean_con_filtered,
      time_to_plateau_inj, time_to_plateau_con
    """

    # Se uno dei DataFrame è vuoto, non calcoliamo nulla
    if df_inj.empty or df_con.empty:
        return df_inj, df_con, {}

    # Copie per filtrare
    df_inj_filtered = df_inj.copy()
    df_con_filtered = df_con.copy()

    # (Opzionale) Filtro Gaussiano sulla colonna d'interesse
    if apply_filter:
        df_inj_filtered[column_for_peak] = gaussian_filter1d(
            df_inj_filtered[column_for_peak],
            sigma=filter_sigma
        )
        df_con_filtered[column_for_peak] = gaussian_filter1d(
            df_con_filtered[column_for_peak],
            sigma=filter_sigma
        )

    # Trova picco injection filtrata
    peak_idx_inj = df_inj_filtered[column_for_peak].idxmax()
    peak_inj_value = df_inj_filtered.loc[peak_idx_inj, column_for_peak]
    peak_inj_time_s = df_inj_filtered.loc[peak_idx_inj, time_column]

    # Trova picco controlaterale filtrata
    peak_idx_con = df_con_filtered[column_for_peak].idxmax()
    peak_con_value = df_con_filtered.loc[peak_idx_con, column_for_peak]
    peak_con_time_s = df_con_filtered.loc[peak_idx_con, time_column]

    # Calcolo media injection e controlaterale filtrate
    mean_inj = df_inj_filtered[column_for_peak].mean()
    mean_con = df_con_filtered[column_for_peak].mean()

    # Calcolo tempo al plateau (primo tempo in cui dose >= plateau_fraction * picco)
    def time_to_plateau(df, peak_val):
        # Soglia: 90% del picco (o plateau_fraction se personalizzato)
        threshold = plateau_fraction * peak_val
        mask = df[column_for_peak] >= threshold
        if mask.any():
            # idx della prima riga True
            idx_first = mask.idxmax()  
            return df.loc[idx_first, time_column]
        return None  # Se non raggiunge mai la soglia

    time_to_plateau_inj = time_to_plateau(df_inj_filtered, peak_inj_value)
    time_to_plateau_con = time_to_plateau(df_con_filtered, peak_con_value)

    # Creiamo il dizionario con le statistiche
    stats = {
        "peak_inj_time_s": peak_inj_time_s,
        "peak_inj_value": peak_inj_value,
        "peak_con_time_s": peak_con_time_s,
        "peak_con_value": peak_con_value,
        "mean_inj_filtered": mean_inj,
        "mean_con_filtered": mean_con,
        "time_to_plateau_inj": time_to_plateau_inj,
        "time_to_plateau_con": time_to_plateau_con
    }

    return df_inj_filtered, df_con_filtered, stats


