# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 09:26:59 2025

@author: PANICON
"""

# -*- coding: utf-8 -*-
"""
DiagnosticAnalysis – versione rivista (2025‑04‑28, build B‑full)

* Start basato sulla pendenza (5 %·peak / s per ≥ 4 s)
* Picco massimo nei primi 120 s dallo start
* Plateau = derivata < 2 %·peak / s per ≥ 30 s
* Metriche robuste a stravaso (min peak/plateau = 1.2)
* Filtra curve di puro fondo (peak < 1 µSv/h)
* Completa di plot_results e ritorni corretti.
"""

from analysis.base_analysis import BaseAnalysis
from peak_analysis import analyze_peak
from plot_manager import plot_injection_controlateral
from additional_metrics import compute_additional_metrics

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, peak_prominences

# -----------------------------------------------------------------------------
# Parametri configurabili
# -----------------------------------------------------------------------------
PEAK_SEARCH_MAX_S = 120          # picco cercato nei primi 2 min
SLOPE_RISE_FRAC = 0.05           # 5 %·peak/s per start
RISE_WIN_S = 4                   # pendenza stabile ≥ 4 s
PEAK_PROM_FRAC = 0.05            # prominenza minima 5 %
PEAK_OFFSET_MIN_S = 30           # attendi 30 s prima di cercare plateau
SLOPE_PLAT_FRAC = 0.02           # plateau: derivata < 2 %·peak/s
STABLE_WIN_S = 30                # plateau stabile ≥ 30 s
WINDOW_AFTER_PEAK_S = 200        # analizza max 3.5 min post‑picco
PLATEAU_TAIL_S = None            # opz. media solo coda plateau
MIN_PEAK_OVER_PLATEAU = 1.2      # accetta stravaso
MIN_ABS_PEAK = 1.0               # µSv/h sotto cui si skippa
# -----------------------------------------------------------------------------


def _consecutive_true_blocks(mask: np.ndarray, times: np.ndarray, min_duration: float):
    """Restituisce liste (t_start, t_end) dove mask True per ≥ min_duration."""
    if not mask.any():
        return []
    idx = np.flatnonzero(mask)
    starts = [idx[0]]
    for i in range(1, len(idx)):
        if idx[i] != idx[i - 1] + 1:
            starts.append(idx[i])
    blocks = []
    for s in starts:
        e = s
        while e + 1 < len(mask) and mask[e + 1]:
            e += 1
        if times[e] - times[s] >= min_duration:
            blocks.append((times[s], times[e]))
    return blocks


def analyze_injection_like_diagnostic(df_inj,
                                      dose_col="dose_rate",
                                      time_col="time_seconds"):
    """
    Applica ESATTAMENTE la logica diagnostica (start su slope, picco ≤120s,
    finestra fino a peak_time+WINDOW_AFTER_PEAK_S, plateau da slope stabile).
    Ritorna: df_inj_filtered, stats, meta (rise_start_t, peak_time, plateau_start_t).
    """
    import numpy as np
    from scipy.signal import find_peaks, peak_prominences
    from peak_analysis import analyze_peak as _ap

    if df_inj.empty:
        return pd.DataFrame(), {}, {}

    # 1) smoothing leggero come in diagnostica
    df_inj_f, _dummy, _ = _ap(
        df_inj, df_inj,
        column_for_peak=dose_col,
        time_column=time_col,
        apply_filter=True,
        filter_sigma=3.0,
        plateau_fraction=0.85,
    )

    # 2) start su slope
    dy = np.gradient(df_inj_f[dose_col].values)
    dt = np.gradient(df_inj_f[time_col].values)
    slope = dy / dt
    peak_global = df_inj_f[dose_col].max()
    slope_thr = SLOPE_RISE_FRAC * peak_global
    rise_blocks = _consecutive_true_blocks(
        slope >= slope_thr, df_inj_f[time_col].values, RISE_WIN_S
    )
    rise_start_t = rise_blocks[0][0] if rise_blocks else df_inj_f[time_col].iloc[0]

    # tronca e azzera tempo
    df_inj_f = df_inj_f[df_inj_f[time_col] >= rise_start_t].copy()
    df_inj_f[time_col] -= rise_start_t

    # 3) picco entro 120 s
    win = df_inj_f[df_inj_f[time_col] <= PEAK_SEARCH_MAX_S]
    if win.empty:
        return pd.DataFrame(), {}, {}
    peaks, _ = find_peaks(win[dose_col].values)
    if len(peaks):
        prom = peak_prominences(win[dose_col].values, peaks)[0]
        valid = [p for p, pr in zip(peaks, prom) if pr >= PEAK_PROM_FRAC * win[dose_col].max()]
        peak_idx = win.index[valid[0]] if valid else win.index[peaks[0]]
    else:
        peak_idx = win[dose_col].idxmax()
    peak_time = float(df_inj_f.loc[peak_idx, time_col])
    peak_val  = float(df_inj_f.loc[peak_idx, dose_col])

    if peak_val < MIN_ABS_PEAK:
        # curva a fondo
        return pd.DataFrame(), {}, {"rise_start_t": float(rise_start_t), "peak_time": float(peak_time)}

    # 4) finestra totale
    df_inj_f = df_inj_f[df_inj_f[time_col] <= peak_time + WINDOW_AFTER_PEAK_S].copy()

    # 5) plateau: slope < 2%·peak/s per ≥30 s (da 30 s post-picco)
    post = df_inj_f[df_inj_f[time_col] >= peak_time + PEAK_OFFSET_MIN_S]
    if post.empty:
        plateau_start_t = peak_time + PEAK_OFFSET_MIN_S
    else:
        slope_post = np.abs(np.gradient(post[dose_col].values) / np.gradient(post[time_col].values))
        blocks = _consecutive_true_blocks(slope_post < SLOPE_PLAT_FRAC * peak_val,
                                          post[time_col].values, STABLE_WIN_S)
        plateau_start_t = float(blocks[0][0]) if blocks else (peak_time + PEAK_OFFSET_MIN_S)

    plateau_inj = df_inj_f[df_inj_f[time_col] >= plateau_start_t]
    mean_pl_inj = float(plateau_inj[dose_col].mean())

    # 6) ricalcolo picco se troppo vicino al plateau
    if mean_pl_inj > 0 and peak_val < MIN_PEAK_OVER_PLATEAU * mean_pl_inj:
        pre = df_inj_f[df_inj_f[time_col] < plateau_start_t]
        if not pre.empty:
            peak_idx = pre[dose_col].idxmax()
            peak_time = float(df_inj_f.loc[peak_idx, time_col])
            peak_val  = float(df_inj_f.loc[peak_idx, dose_col])

    # 7) metriche injection
    stats = {
        "peak_inj_time_s": peak_time,
        "peak_inj_value": peak_val,
        "plateau_start_time_s": plateau_start_t,
        "mean_plateau_inj": mean_pl_inj,
        "delta_dose": peak_val - mean_pl_inj,
        "ratio_dose": (peak_val - mean_pl_inj) / peak_val if peak_val else None,
        "time_to_plateau_inj": plateau_start_t - peak_time,
    }
    stats = compute_additional_metrics(df_inj_f, stats, time_column=time_col, dose_column=dose_col)

    meta = {"rise_start_t": float(rise_start_t), "peak_time": float(peak_time), "plateau_start_t": float(plateau_start_t)}
    return df_inj_f, stats, meta


class DiagnosticAnalysis(BaseAnalysis):
    """Pipeline diagnostica con algoritmo robusto a stravaso."""

    # --------------------------------------------------- colonne mapping
    def get_injection_columns(self):
        from config import COLUMNS_INJECTION_DIAGNOSTIC
        return COLUMNS_INJECTION_DIAGNOSTIC

    def get_controlateral_columns(self):
        from config import COLUMNS_CONTROLATERAL_DIAGNOSTIC
        return COLUMNS_CONTROLATERAL_DIAGNOSTIC

    # --------------------------------------------------- load & align
    def load_data(self, inj_path, con_path):
        dm = self.data_manager
        return dm.load_and_clean_data(inj_path, self.get_injection_columns()), \
               dm.load_and_clean_data(con_path, self.get_controlateral_columns())

    def synchronize_and_align(self, df_inj, df_con, base_name):
        dm = self.data_manager
        df_inj_s, df_con_s = dm.synchronize_data(df_inj, df_con, base_name)
        return dm.align_with_injection_reference(df_inj_s, df_con_s, total_minutes=15)

    # --------------------------------------------------- core metrics
    def analyze_peak(self, df_inj, df_con):
        if df_inj.empty or df_con.empty:
            return df_inj, df_con, {}

        # 1. filtro gaussiano
        df_inj_f, df_con_f, _ = analyze_peak(
            df_inj, df_con,
            column_for_peak="dose_rate",
            time_column="time_seconds",
            apply_filter=True,
            filter_sigma=3.0,
            plateau_fraction=0.85,
        )
        col, tcol = "dose_rate", "time_seconds"

        # 2. start basato su slope
        dy = np.gradient(df_inj_f[col].values)
        dt = np.gradient(df_inj_f[tcol].values)
        slope = dy / dt
        peak_global = df_inj_f[col].max()
        slope_thr = SLOPE_RISE_FRAC * peak_global
        rise_blocks = _consecutive_true_blocks(slope >= slope_thr, df_inj_f[tcol].values, RISE_WIN_S)
        rise_start_t = rise_blocks[0][0] if rise_blocks else df_inj_f[tcol].iloc[0]

        # tronca e azzera tempo
        df_inj_f = df_inj_f[df_inj_f[tcol] >= rise_start_t].copy()
        df_con_f = df_con_f[df_con_f[tcol] >= rise_start_t].copy()
        df_inj_f[tcol] -= rise_start_t
        df_con_f[tcol] -= rise_start_t

        # 3. picco entro 120 s
        win = df_inj_f[df_inj_f[tcol] <= PEAK_SEARCH_MAX_S]
        if win.empty:
            return df_inj_f, df_con_f, {}
        peaks, _ = find_peaks(win[col].values)
        if len(peaks):
            prom = peak_prominences(win[col].values, peaks)[0]
            valid = [p for p, pr in zip(peaks, prom) if pr >= PEAK_PROM_FRAC * win[col].max()]
            peak_idx = win.index[valid[0]] if valid else win.index[peaks[0]]
        else:
            peak_idx = win[col].idxmax()
        peak_time = df_inj_f.loc[peak_idx, tcol]
        peak_val = df_inj_f.loc[peak_idx, col]

        if peak_val < MIN_ABS_PEAK:
            print("Curve a fondo – skip")
            return pd.DataFrame(), pd.DataFrame(), {}

        # 4. restringi finestra totale
        df_inj_f = df_inj_f[df_inj_f[tcol] <= peak_time + WINDOW_AFTER_PEAK_S].copy()
        df_con_f = df_con_f[df_con_f[tcol] <= peak_time + WINDOW_AFTER_PEAK_S].copy()

        # 5. plateau via slope
        post = df_inj_f[df_inj_f[tcol] >= peak_time + PEAK_OFFSET_MIN_S]
        if post.empty:
            plateau_start_t = peak_time + PEAK_OFFSET_MIN_S
        else:
            slope_post = np.abs(np.gradient(post[col].values) / np.gradient(post[tcol].values))
            blocks = _consecutive_true_blocks(slope_post < SLOPE_PLAT_FRAC * peak_val,
                                              post[tcol].values, STABLE_WIN_S)
            plateau_start_t = blocks[0][0] if blocks else peak_time + PEAK_OFFSET_MIN_S

        plateau_inj = df_inj_f[df_inj_f[tcol] >= plateau_start_t]
        if PLATEAU_TAIL_S:
            plateau_inj = plateau_inj[plateau_inj[tcol] >= plateau_inj[tcol].max() - PLATEAU_TAIL_S]
        mean_pl_inj = plateau_inj[col].mean()

        plateau_con = df_con_f[df_con_f[tcol] >= plateau_start_t]
        if PLATEAU_TAIL_S:
            plateau_con = plateau_con[plateau_con[tcol] >= plateau_con[tcol].max() - PLATEAU_TAIL_S]
        mean_pl_con = plateau_con[col].mean()

        # 6. eventuale ricalcolo picco se troppo vicino plateau
        if mean_pl_inj > 0 and peak_val < MIN_PEAK_OVER_PLATEAU * mean_pl_inj:
            pre = df_inj_f[df_inj_f[tcol] < plateau_start_t]
            if not pre.empty:
                peak_idx = pre[col].idxmax()
                peak_time = df_inj_f.loc[peak_idx, tcol]
                peak_val = df_inj_f.loc[peak_idx, col]

        # 7. metriche
        stats = {
            "peak_inj_time_s": peak_time,
            "peak_inj_value": peak_val,
            "plateau_start_time_s": plateau_start_t,
            "mean_plateau_inj": mean_pl_inj,
            "mean_plateau_con": mean_pl_con,
            "delta_dose": peak_val - mean_pl_inj,
            "ratio_dose": (peak_val - mean_pl_inj) / peak_val if peak_val else None,
            "time_to_plateau_inj": plateau_start_t - peak_time,
        }
        stats = compute_additional_metrics(df_inj_f, stats, time_column=tcol, dose_column=col)
        return df_inj_f, df_con_f, stats

    # --------------------------------------------------- plot
    def plot_results(self, base_name, df_inj, df_con, df_inj_filtered, df_con_filtered):
        from config import PATH_GRAFICI_DIAGNOSTIC
        plot_injection_controlateral(
            base_name=f"{base_name}_filtered",
            df_inj=df_inj_filtered,
            df_con=df_con_filtered,
            output_dir=PATH_GRAFICI_DIAGNOSTIC,
            yscale="log",
            dose_column="dose_rate",
            time_column="time_seconds",
        )
