# inj_only_analysis.py
from analysis.base_analysis import BaseAnalysis
from peak_analysis import analyze_peak   # usa il filtro gaussiano
from additional_metrics import compute_additional_metrics
import numpy as np
import pandas as pd

MIN_ABS_PEAK = 1.0  # µSv/h, come diagnostica

class InjectionOnlyAnalysis(BaseAnalysis):
    """
    Analisi con un solo dosimetro (injection). Usa le stesse euristiche della diagnostica
    per start/peak/plateau, ma ignora il controlaterale.
    Colonne attese: time ('timestamp' alias) e dose_rate.
    Output: Stats (peak, plateau, delta_dose, ratio_dose, area_after_peak, slope_rising).
    """

    # mappature colonne: riuso alias diagnostica
    def get_injection_columns(self):
        from config import COLUMNS_INJECTION_DIAGNOSTIC
        return COLUMNS_INJECTION_DIAGNOSTIC

    # per compatibilità con BaseAnalysis, ma non verrà usato
    def get_controlateral_columns(self):
        return {"time": ["timestamp", "Timestamp"], "dose_rate": ["dose_rate"]}

    # solo injection
    def load_data(self, inj_path, con_path=None):
        df_inj = self.data_manager.load_and_clean_data(inj_path, self.get_injection_columns())
        return df_inj, pd.DataFrame()

    # nessuna sincro con controlaterale
    def synchronize_and_align(self, df_inj, df_con, base_name):
        # allinea solo sull’injection; usa una copia come “dummy” controlaterale
        dm = self.data_manager
        inj_aligned, _ = dm.align_with_injection_reference(df_inj, df_inj, total_minutes=15)
        return inj_aligned, inj_aligned.copy()

    def analyze_peak(self, df_inj, _df_con_not_used):
        if df_inj.empty:
            return df_inj, pd.DataFrame(), {}
        # filtro + picco (riuso funzione generica ma passeremo solo df_inj)
        df_inj_f = df_inj.copy()
        # colonna e tempo
        col, tcol = "dose_rate", "time_seconds"

        # semplice smoothing leggero
        from scipy.ndimage import gaussian_filter1d
        df_inj_f[col] = gaussian_filter1d(df_inj_f[col].values, sigma=3.0)

        peak_idx = df_inj_f[col].idxmax()
        peak_val = df_inj_f.loc[peak_idx, col]
        peak_time = df_inj_f.loc[peak_idx, tcol]
        if peak_val < MIN_ABS_PEAK:
            print("Curve a fondo – inj only – skip")
            return pd.DataFrame(), pd.DataFrame(), {}

        # stima plateau: media in coda (ultimi 30 s) oppure derivata < 2%·peak/s per ≥30 s
        tail = df_inj_f.iloc[-30:] if len(df_inj_f) >= 30 else df_inj_f
        mean_pl_inj = float(tail[col].mean())

        stats = {
            "peak_inj_time_s": float(peak_time),
            "peak_inj_value": float(peak_val),
            "mean_plateau_inj": mean_pl_inj,
            "delta_dose": float(peak_val - mean_pl_inj),
            "ratio_dose": float((peak_val - mean_pl_inj) / peak_val) if peak_val else np.nan,
        }
        stats = compute_additional_metrics(df_inj_f, stats, time_column=tcol, dose_column=col)
        dummy_con_f = df_inj_f.copy()
        return df_inj_f, dummy_con_f, stats

    def plot_results(self, base_name, df_inj, _df_con, df_inj_filtered, _df_con_filtered):
        # plot 1 solo dosimetro (riuso plot_manager ma passiamo la stessa curva su 2 tracce)
        from plot_manager import plot_injection_controlateral
        from config import PATH_GRAFICI_DIAGNOSTIC

        dummy = df_inj_filtered[[c for c in df_inj_filtered.columns]] .copy()
        plot_injection_controlateral(
            base_name=f"{base_name}_injonly",
            df_inj=df_inj_filtered,
            df_con=dummy,  # tratteggiata uguale (solo per comodità visiva)
            output_dir=PATH_GRAFICI_DIAGNOSTIC,
            yscale="log",
            dose_column="dose_rate",
            time_column="time_seconds",
        )
