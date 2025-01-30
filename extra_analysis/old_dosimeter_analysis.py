# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 15:21:33 2025

@author: panicon
"""

# old_dosimeter_analysis.py (dentro code/utility_and_extra_analysis/)


    
import os    
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# Importiamo i path dal config
from ..main.config import ROOT_STRAVASO , PATH_STRAVASO_PLOTS

class OldDataManager:
    def __init__(
        self,
        injection_legacy_dir=None,
        controlateral_legacy_dir=None,
        output_plot_dir=None,
        time_col="Timestamp",
        dose_col="DR_Max",
        minutes=15
    ):
        """
        Inizializza i path di default importandoli da config (ROOT_STRAVASO, PATH_STRAVASO_PLOTS).
        Se injection_legacy_dir o controlateral_legacy_dir non vengono specificati,
        usiamo ROOT_STRAVASO + "/injections" e "/controlaterals" (oppure li definisci tu).

        :param injection_legacy_dir: cartella con i file excel "injection" vecchio format.
        :param controlateral_legacy_dir: cartella con i file excel "controlateral" vecchio format.
        :param output_plot_dir: cartella dove salvare i plot. Di default, PATH_STRAVASO_PLOTS.
        :param time_col: nome colonna timestamp (es. "Timestamp").
        :param dose_col: nome colonna dose (es. "DR_Max").
        :param minutes: quanti minuti di dati estrarre dall'inizio (default 15).
        """
        # Se non passano nulla, usiamo ROOT_STRAVASO come base e creiamo subcartelle
        if injection_legacy_dir is None:
            injection_legacy_dir = os.path.join(ROOT_STRAVASO, "injections")
        if controlateral_legacy_dir is None:
            controlateral_legacy_dir = os.path.join(ROOT_STRAVASO, "controlaterals")
        if output_plot_dir is None:
            output_plot_dir = PATH_STRAVASO_PLOTS

        self.injection_legacy_dir = injection_legacy_dir
        self.controlateral_legacy_dir = controlateral_legacy_dir
        self.output_plot_dir = output_plot_dir
        self.time_col = time_col
        self.dose_col = dose_col
        self.minutes = minutes

        # Creo la cartella per i plot se non esiste
        os.makedirs(self.output_plot_dir, exist_ok=True)

    def get_file_pairs(self):
        """
        Scansione cartelle injection_legacy_dir e controlateral_legacy_dir,
        trova i file .xlsx o csv, cerca matching sul nome base.
        """
        inj_files = [f for f in os.listdir(self.injection_legacy_dir) if f.endswith(".xlsx")]
        con_files = [f for f in os.listdir(self.controlateral_legacy_dir) if f.endswith(".xlsx")]

        pairs = []
        for injf in inj_files:
            # Esempio di convenzione: "paziente01_inj_legacy.xlsx" e "paziente01_cont_legacy.xlsx"
            # Adatta alla convenzione reale
            base = injf.replace("_inj_legacy.xlsx", "")
            cont_name = base + "_cont_legacy.xlsx"

            if cont_name in con_files:
                pairs.append((base, injf, cont_name))
            else:
                print(f"Manca il controlateral per {base}!")
        return pairs

    def load_and_clean_old_excel(self, path):
        """
        Carica un file Excel, ordina i Timestamp, seleziona i primi 'self.minutes' minuti,
        e mantiene solo la colonna dose (dose_col).
        Ritorna un DataFrame con ['dose', 'time_seconds'].
        """
        try:
            df = pd.read_excel(path)
        except Exception as e:
            print(f"Errore caricando {path}: {e}")
            return None

        # 1) Converto il timestamp e ordino
        if self.time_col in df.columns:
            df[self.time_col] = pd.to_datetime(df[self.time_col], errors='coerce')
            df.dropna(subset=[self.time_col], inplace=True)
            df.sort_values(by=self.time_col, inplace=True)
        else:
            print(f"Colonna {self.time_col} non trovata in {path}.")
            return None

        df.set_index(self.time_col, drop=True, inplace=True)
        if len(df) == 0:
            return None

        # 2) Taglia i primi self.minutes
        start_time = df.index[0]
        end_time = start_time + pd.Timedelta(minutes=self.minutes)
        df = df.loc[df.index <= end_time].copy()
        if len(df) == 0:
            print(f"Nessun dato nei primi {self.minutes} min in {path}!")
            return None

        # 3) Controllo colonna dose
        if self.dose_col not in df.columns:
            print(f"Colonna dose '{self.dose_col}' non trovata in {path}!")
            return None

        # Rinomino colonna dose => "dose"
        df.rename(columns={self.dose_col: "dose"}, inplace=True)

        # 4) Aggiungo 'time_seconds'
        df["time_seconds"] = (df.index - start_time).total_seconds()

        return df[["dose", "time_seconds"]]

    def filter_and_plot(self, df_inj, df_con, base_name, sigma=5):
        """
        Filtra con gaussian_filter1d le colonne 'dose' e plotta injection vs controlateral
        in scala log. Salva nel self.output_plot_dir/base_name.png.
        """
        if df_inj is None or df_con is None or len(df_inj)==0 or len(df_con)==0:
            print(f"Dati vuoti per {base_name}, skip plot.")
            return

        df_inj["dose_filt"] = gaussian_filter1d(df_inj["dose"], sigma=sigma)
        df_con["dose_filt"] = gaussian_filter1d(df_con["dose"], sigma=sigma)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df_inj["time_seconds"], df_inj["dose_filt"], label="Injection", color='orange')
        ax.plot(df_con["time_seconds"], df_con["dose_filt"], label="Controlateral", color='blue', linestyle='--')

        ax.set_yscale("log")
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Dose [filtered]")
        ax.set_title(f"Legacy Data - {base_name}")
        ax.legend()
        ax.grid(True)

        outpath = os.path.join(self.output_plot_dir, f"{base_name}.png")
        plt.savefig(outpath)
        plt.close(fig)
        print(f"Plot salvato in: {outpath}")

    def run(self):
        """
        Metodo principale che:
         - trova i file pairs
         - carica e pulisce (inj, con)
         - plotta
        """
        pairs = self.get_file_pairs()
        for base_name, injf, conf in pairs:
            inj_path = os.path.join(self.injection_legacy_dir, injf)
            con_path = os.path.join(self.controlateral_legacy_dir, conf)

            df_inj = self.load_and_clean_old_excel(inj_path)
            df_con = self.load_and_clean_old_excel(con_path)
            if df_inj is None or df_con is None:
                print(f"Skip {base_name} per dati non validi.")
                continue

            self.filter_and_plot(df_inj, df_con, base_name, sigma=5)


if __name__ == "__main__":
    # Esempio di utilizzo
    manager = OldDataManager()
    manager.run()
