# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 16:53:28 2025

@author: nicop
"""

# plot_manager.py

import os
import matplotlib.pyplot as plt

def plot_injection_controlateral(
    base_name,
    df_inj,
    df_con,
    output_dir,
    yscale='log',
    dose_column='Dose (μSv)',
    time_column='time_seconds'
):
    """
    Esegue un plot di df_inj e df_con (Dose vs time).
    :param base_name: Nome del caso, usato per salvare il file.
    :param df_inj: DataFrame injection (deve contenere time_column e dose_column).
    :param df_con: DataFrame controlateral (idem).
    :param output_dir: cartella in cui salvare il plot (es. 'grafici').
    :param yscale: 'linear' o 'log' per la scala y.
    :param dose_column: nome della colonna che contiene la dose (default 'Dose (μSv)').
    :param time_column: nome della colonna per il tempo (default 'time_seconds').
    """

    # Se le colonne non esistono nel DataFrame, avvisa e ritorna
    if time_column not in df_inj.columns or dose_column not in df_inj.columns:
        print(f"Attenzione: df_inj non contiene {time_column} o {dose_column}")
        return
    if time_column not in df_con.columns or dose_column not in df_con.columns:
        print(f"Attenzione: df_con non contiene {time_column} o {dose_column}")
        return

    # Crea la figura
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot injection
    ax.plot(df_inj[time_column], df_inj[dose_column], label='Injection', color='orange')

    # Plot controlateral
    ax.plot(df_con[time_column], df_con[dose_column], label='Controlateral', color='blue', linestyle='--')

    # Impostazioni assi
    ax.set_xlabel("Time [s]", fontsize=14)
    ax.set_ylabel(dose_column, fontsize=14)
    ax.set_yscale(yscale)
    ax.legend(fontsize=12)
    ax.grid(True)

    # Titolo (se vuoi)
    ax.set_title(f"Confronto Injection vs Controlateral - {base_name}", fontsize=16)

    # Salvataggio
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
