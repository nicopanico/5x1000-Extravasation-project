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
    df_inj,
    df_con,
    column_for_peak="Dose (μSv)",
    time_column="time_seconds",
    margin_before=60,
    margin_after=540,
    apply_filter=False,
    filter_sigma=5
):
    """
    Funzione che orchestra i passi:
    1) trova il picco in df_inj[column_for_peak]
    2) definisce start_time = peak_time_s - margin_before, end_time = peak_time_s + margin_after
    3) slice i due DF
    4) opzionalmente filtra la colonna
    5) calcola statistiche e restituisce (df_inj_slice, df_con_slice, stats)
    """
    peak_idx, peak_time_s, peak_val = find_peak(df_inj, column_for_peak, time_column)
    if peak_time_s is None:
        # df_inj era vuoto
        return df_inj, df_con, {}

    start_time = peak_time_s - margin_before
    end_time = peak_time_s + margin_after

    df_inj_slice = slice_data(df_inj, time_column, start_time, end_time)
    df_con_slice = slice_data(df_con, time_column, start_time, end_time)

    if apply_filter:
        df_inj_slice = apply_gaussian_filter_to_column(df_inj_slice, column_for_peak, sigma=filter_sigma)
        df_con_slice = apply_gaussian_filter_to_column(df_con_slice, column_for_peak, sigma=filter_sigma)

    stats = compute_stats(df_inj_slice, df_con_slice, column_for_peak)
    # puoi aggiungere altre statistiche, integrali, etc.

    return df_inj_slice, df_con_slice, stats
