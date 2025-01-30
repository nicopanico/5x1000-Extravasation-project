# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 11:09:39 2025

@author: panicon
"""

# delta_analysis.py
import pandas as pd
import numpy as np

def compute_delta_timepoints(
    df_inj_filtered: pd.DataFrame,
    df_con_filtered: pd.DataFrame,
    base_name: str,
    column: str = "Intensità di dose (μSv/h)",
    time_points=None,
    offset: int = 60
):
    """
    Calcola la differenza assoluta Delta(t) = |inj(t) - con(t)| 
    su 'column', partendo da 'offset' secondi.
    Per i time_points (lista di secondi relative a 'offset'), estrae i valori di Delta
    e calcola la media.

    Ritorna un DataFrame monoriga con:
      base_name, delta_60, delta_120, ..., mean_delta
    Esempio:
      time_points = [0, 60, 120, 180, ...] -> corrispondono a offset + x
      Se offset=60 e x=60 -> corrisponde a t=120s nel dataset globale.
    """
    if time_points is None:
        # Valori di default
        time_points = [0, 60, 120, 180, 240, 300, 360, 480, 600]

    # Assicuriamoci di avere la stessa lunghezza
    min_len = min(len(df_inj_filtered), len(df_con_filtered))
    df_inj_filtered = df_inj_filtered.iloc[:min_len].copy()
    df_con_filtered = df_con_filtered.iloc[:min_len].copy()

    # Calcolo differenza
    inj_series = df_inj_filtered[column]
    con_series = df_con_filtered[column]
    delta_series = abs(inj_series - con_series)

    # Tagliamo i primi 'offset' secondi
    if offset < min_len:
        delta_subset = delta_series.iloc[offset:].reset_index(drop=True)
    else:
        # Se offset > min_len, avremo un DF vuoto
        delta_subset = pd.Series([], dtype=float)

    results = {"base_name": base_name}

    # estrai i valori in delta_subset
    for x in time_points:
        idx = x  # x=0 corrisponde a second=offset nel dataset globale
        col_name = f"delta_{offset + x}"  # ad es. delta_120
        if idx < len(delta_subset):
            val = delta_subset.iloc[idx]
        else:
            val = np.nan
        results[col_name] = val

    # media su quei time_points
    arr_vals = [results[f"delta_{offset + x}"] for x in time_points if not pd.isna(results[f"delta_{offset + x}"])]
    mean_val = np.mean(arr_vals) if len(arr_vals) > 0 else np.nan
    results["mean_delta"] = mean_val

    return pd.DataFrame([results])
