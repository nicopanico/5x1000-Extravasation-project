# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 16:53:28 2025

@author: nicop
"""

# plot_manager.py

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_injection_controlateral(
    base_name,
    df_inj,
    df_con,
    output_dir,
    yscale='log',
    dose_column='Dose (μSv)',
    time_column='time_seconds',
    stats=None,       # Statistiche generali
    ratio_stats=None  # Statistiche ratio
):
    fig, ax = plt.subplots(figsize=(10,6))

    ax.plot(df_inj[time_column], df_inj[dose_column], label='Injection', color='orange')
    ax.plot(df_con[time_column], df_con[dose_column], label='Controlateral', color='blue', linestyle='--')

    ax.set_yscale(yscale)
    ax.set_xlabel("Time [s]", fontsize=14)
    ax.set_ylabel(dose_column, fontsize=14)
    ax.set_title(f"Confronto Injection vs Controlateral - {base_name}", fontsize=16)
    ax.legend()
    ax.grid(True)

    # Annotazioni dalle statistiche generali (es. t_90 e slope)
    if stats is not None:
        # Annotazione per t_90 dell'injection
        t_90_inj = stats.get("time_to_90pct_inj", None)
        if t_90_inj is not None and not pd.isna(t_90_inj):
            idx_inj = (df_inj[time_column] - t_90_inj).abs().idxmin()
            y_val_inj = df_inj.loc[idx_inj, dose_column]
            ax.axvline(x=t_90_inj, color='red', linestyle='--', alpha=0.7, label='t_90_inj')
            ax.scatter(t_90_inj, y_val_inj, color='red', marker='x')
            ax.text(t_90_inj, y_val_inj, f"t_90_inj={t_90_inj:.0f}s", color='red', fontsize=9, ha='left')

        # Annotazione per t_90 della controlateral
        t_90_con = stats.get("time_to_90pct_con", None)
        if t_90_con is not None and not pd.isna(t_90_con):
            idx_con = (df_con[time_column] - t_90_con).abs().idxmin()
            y_val_con = df_con.loc[idx_con, dose_column]
            ax.axvline(x=t_90_con, color='green', linestyle='--', alpha=0.7, label='t_90_con')
            ax.scatter(t_90_con, y_val_con, color='green', marker='o')
            ax.text(t_90_con, y_val_con, f"t_90_con={t_90_con:.0f}s", color='green', fontsize=9, ha='left')

        # Annotazione per la slope iniziale
        slope_inj = stats.get("slope_inj_0_120s", None)
        if slope_inj is not None:
            ax.text(0.02, 0.9, f"Slope(0-120s)={slope_inj:.2f}",
                    transform=ax.transAxes, color='magenta', fontsize=10)

    # Annotazioni per le metriche ratio (salvate in ratio_stats)
    if ratio_stats is not None:
        ratio_mean = ratio_stats.get("ratio_intervals_mean", None)
        if ratio_mean is not None and not np.isnan(ratio_mean):
            ax.text(0.02, 0.85, f"Ratio mean={ratio_mean:.2f}",
                    transform=ax.transAxes, color='green', fontsize=10)
        ratio_max = ratio_stats.get("ratio_max", None)
        if ratio_max is not None and not np.isnan(ratio_max):
            ax.text(0.02, 0.80, f"Ratio max={ratio_max:.2f}",
                    transform=ax.transAxes, color='green', fontsize=10)

    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, f"plot_{base_name}.png")
    plt.savefig(plot_path)
    plt.close(fig)
    print(f"Plot salvato in: {plot_path}")




def plot_comparison_raw_filtered(
    base_name,
    df_inj_raw,
    df_inj_filt,
    df_con_raw,
    df_con_filt,
    output_dir,
    dose_column="Dose (μSv)",
    time_column="time_seconds",
    yscale="log"
):
    import matplotlib.pyplot as plt
    import os

    fig, ax = plt.subplots(figsize=(10,6))

    ax.plot(df_inj_raw[time_column], df_inj_raw[dose_column], label='Inj RAW', color='orange')
    ax.plot(df_inj_filt[time_column], df_inj_filt[dose_column], label='Inj FILTERED', color='red')

    ax.plot(df_con_raw[time_column], df_con_raw[dose_column], label='Con RAW', color='blue', linestyle='--')
    ax.plot(df_con_filt[time_column], df_con_filt[dose_column], label='Con FILTERED', color='green', linestyle='--')

    ax.set_yscale(yscale)
    ax.set_xlabel("Time [s]", fontsize=14)
    ax.set_ylabel(dose_column, fontsize=14)
    ax.set_title(f"Confronto RAW vs FILTERED - {base_name}", fontsize=16)
    ax.legend()
    ax.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, f"plot_{base_name}_comparison_raw_filtered.png"))
    plt.close(fig)
