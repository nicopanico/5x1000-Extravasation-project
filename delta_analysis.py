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
    time_points: list = None,
    offset: int = 60,
    mode: str = "therapy"
):
    """
    Calcola la differenza assoluta Delta(t) = |inj(t) - con(t)| sulla colonna specificata,
    a partire da un offset (in secondi) e per i time_points relativi a quell'offset.
    
    Se i time_points non sono specificati, vengono impostati automaticamente come una suddivisione
    dell'intervallo totale in passi di 60 secondi:
      - Per mode=="therapy": l'intervallo totale è 15 minuti (15*60 secondi)
      - Per mode=="diagnostic": l'intervallo totale è 10 minuti (10*60 secondi)
    
    Args:
        df_inj_filtered (pd.DataFrame): DataFrame dell'iniezione filtrato (la colonna deve contenere valori numerici).
        df_con_filtered (pd.DataFrame): DataFrame del controlateral filtrato.
        base_name (str): Nome base dell'analisi.
        column (str): Nome della colonna su cui calcolare il delta.
        time_points (list, optional): Lista di secondi relativi all'offset. Se None, viene generata automaticamente.
        offset (int): Offset (in secondi) a partire dal quale iniziare l'analisi.
        mode (str): Modalità di analisi: "therapy" o "diagnostic".
        
    Returns:
        pd.DataFrame: Un DataFrame monoriga con i delta per ciascun time_point e la media dei delta.
    """
    # Imposta i time_points default in base alla modalità, se non specificati
    if time_points is None:
        if mode == "therapy":
            total_duration = 15 * 60  # 15 minuti in secondi
        elif mode == "diagnostic":
            total_duration = 10 * 60  # 10 minuti in secondi
        else:
            total_duration = 15 * 60
        time_points = list(range(0, total_duration + 1, 60))
    
    # Assicura che i DataFrame abbiano la stessa lunghezza
    min_len = min(len(df_inj_filtered), len(df_con_filtered))
    df_inj_filtered = df_inj_filtered.iloc[:min_len].copy()
    df_con_filtered = df_con_filtered.iloc[:min_len].copy()

    # Calcola la differenza assoluta per la colonna specificata
    inj_series = df_inj_filtered[column]
    con_series = df_con_filtered[column]
    delta_series = abs(inj_series - con_series)

    # Taglia i primi "offset" elementi
    if offset < min_len:
        delta_subset = delta_series.iloc[offset:].reset_index(drop=True)
    else:
        delta_subset = pd.Series([], dtype=float)

    results = {"base_name": base_name}
    # Estrae i valori di delta per ciascun time_point
    for x in time_points:
        idx = x  # time_point 0 corrisponde al valore in posizione "offset"
        col_name = f"delta_{offset + x}"
        if idx < len(delta_subset):
            val = delta_subset.iloc[idx]
        else:
            val = np.nan
        results[col_name] = val

    # Calcola la media dei delta estratti
    arr_vals = [results[f"delta_{offset + x}"] for x in time_points if not pd.isna(results[f"delta_{offset + x}"])]
    mean_val = np.mean(arr_vals) if arr_vals else np.nan
    results["mean_delta"] = mean_val

    return pd.DataFrame([results])
