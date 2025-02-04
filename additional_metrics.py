# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:46:45 2025

@author: PANICON
"""

# additional_metrics.py
import numpy as np

def compute_additional_metrics(df_inj_filtered, stats, time_column='time_seconds', dose_column='dose_rate'):
    """
    Calcola ulteriori metriche sulla curva di dose iniezione:
      - area_after_peak: l'area sotto la curva, integrata dal picco fino alla fine del segmento
      - slope_rising: il tasso di salita (slope) stimato dalla prima misurazione al picco

    Args:
        df_inj_filtered (pd.DataFrame): DataFrame dei dati iniezione filtrati, con colonne per il tempo e la dose.
        stats (dict): Dizionario contenente almeno le chiavi "peak_inj_time_s" e "peak_inj_value".
        time_column (str): Nome della colonna dei tempi (default "time_seconds").
        dose_column (str): Nome della colonna dei valori di dose (default "dose_rate").

    Returns:
        dict: Il dizionario stats aggiornato con le chiavi 'area_after_peak' e 'slope_rising'.
    """
    # Se mancano le informazioni sul picco, restituisce NaN per le nuove metriche
    if "peak_inj_time_s" not in stats or "peak_inj_value" not in stats:
        stats['area_after_peak'] = np.nan
        stats['slope_rising'] = np.nan
        return stats

    peak_time = stats["peak_inj_time_s"]

    # Trova l'indice della riga il cui valore nel tempo è il più vicino a peak_time
    peak_idx = df_inj_filtered[time_column].sub(peak_time).abs().idxmin()

    # Calcola l'area sotto la curva dal picco fino alla fine usando il metodo del trapezio
    sub_df = df_inj_filtered.loc[peak_idx:]
    if sub_df.empty:
        area = np.nan
    else:
        area = np.trapz(sub_df[dose_column], sub_df[time_column])
    stats["area_after_peak"] = area

    # Calcola il tasso di salita (slope) dalla prima misurazione al picco
    rising_df = df_inj_filtered.loc[:peak_idx]
    if rising_df.shape[0] < 2:
        slope = np.nan
    else:
        start_time = rising_df.iloc[0][time_column]
        start_dose = rising_df.iloc[0][dose_column]
        delta_time = peak_time - start_time
        slope = (stats["peak_inj_value"] - start_dose) / delta_time if delta_time != 0 else np.nan
    stats["slope_rising"] = slope

    return stats
