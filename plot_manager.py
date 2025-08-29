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

def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def plot_single_injection(
    base_name,
    df,
    output_dir_base,
    yscale="log",
    dose_column="dose_rate",
    time_column="time_seconds",
    stats=None,
    common_ylim=None,      # (ymin, ymax) oppure None
    y_label=None,          # etichetta asse Y con unità
    subdir_name="plot",    # cartella di salvataggio
):
    out_dir = _ensure_dir(os.path.join(output_dir_base, subdir_name))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df[time_column], df[dose_column], label="Injection", linewidth=2)

    ax.set_yscale(yscale)
    if common_ylim is not None:
        ax.set_ylim(*common_ylim)

    # Etichette assi (con unità)
    ax.set_xlabel("Time [s]", fontsize=14)
    if y_label is None:
        # default sensato per inj_only diagnostica
        y_label = "Dose rate [µSv/h]" if dose_column == "dose_rate" else dose_column
    ax.set_ylabel(y_label, fontsize=14)

    ax.set_title(f"Injection only – {base_name}", fontsize=16)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()

    # Annotazioni utili
    if stats:
        pk_t  = stats.get("peak_inj_time_s")
        pk_v  = stats.get("peak_inj_value")
        pl_v  = stats.get("mean_plateau_inj")
        rd    = stats.get("ratio_dose")

        if pk_t is not None and pk_v is not None:
            ax.axvline(pk_t, linestyle="--", alpha=0.6)
            ax.scatter([pk_t], [pk_v], marker="x")
            ax.text(pk_t, pk_v, f" peak={pk_v:.1f}", va="bottom", ha="left", fontsize=9)

        if pl_v is not None:
            ax.axhline(pl_v, linestyle=":", alpha=0.6)
            ax.text(0.02, 0.92, f"plateau≈{pl_v:.1f}", transform=ax.transAxes, fontsize=10)
        if rd is not None:
            ax.text(0.02, 0.86, f"ratio_dose={rd:.2f}", transform=ax.transAxes, fontsize=10)

    out_path = os.path.join(out_dir, f"plot_{base_name}.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Plot salvato in: {out_path}")


def plot_single_injection_normalized(
    base_name,
    df,
    output_dir_base,
    dose_column="dose_rate",
    time_column="time_seconds",
    stats=None,
    subdir_name="normalized_plot",
):
    """
    Curva normalizzata al picco (y = dose/peak). Scala lineare [0,1.05].
    - Stravaso grave: plateau/peak ~ 1  (curva alta)
    - Normale: plateau/peak << 1        (curva bassa)
    """
    out_dir = _ensure_dir(os.path.join(output_dir_base, subdir_name))
    if df.empty:
        return

    peak = float(np.nanmax(df[dose_column].values))
    if not np.isfinite(peak) or peak <= 0:
        return

    y = df[dose_column].values / peak

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df[time_column].values, y, label="Injection / peak", linewidth=2)

    ax.set_ylim(0, 1.05)   # scala comune
    ax.set_xlabel("Time [s]", fontsize=14)
    ax.set_ylabel("Normalized dose rate [1]", fontsize=14)
    ax.set_title(f"Injection only (normalized) – {base_name}", fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Annotazione plateau/peak e ratio_dose
    if stats:
        pl_v  = stats.get("mean_plateau_inj")
        rd    = stats.get("ratio_dose")
        if pl_v is not None and np.isfinite(peak):
            pl_ratio = pl_v / peak
            ax.axhline(pl_ratio, linestyle=":", alpha=0.6)
            ax.text(0.02, 0.92, f"plateau/peak={pl_ratio:.2f}", transform=ax.transAxes, fontsize=10)
        if rd is not None:
            ax.text(0.02, 0.86, f"ratio_dose={rd:.2f}", transform=ax.transAxes, fontsize=10)

    out_path = os.path.join(out_dir, f"plot_{base_name}_normalized.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Plot salvato in: {out_path}")