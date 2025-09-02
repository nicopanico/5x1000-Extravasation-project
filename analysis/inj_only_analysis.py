# inj_only_analysis.py
from analysis.base_analysis import BaseAnalysis
import pandas as pd

class InjectionOnlyAnalysis(BaseAnalysis):
    """
    Analisi con un solo dosimetro (injection). Applica esattamente la logica
    diagnostica (start/peak/plateau) riusando la funzione condivisa in
    diagnostic_analysis. Restituisce un 'dummy' controlaterale per compatibilità
    con la pipeline base.
    """

    # mappature colonne: riuso alias diagnostica
    def get_injection_columns(self):
        from config import COLUMNS_INJECTION_DIAGNOSTIC
        return COLUMNS_INJECTION_DIAGNOSTIC

    # per compatibilità con BaseAnalysis (non usato in inj_only)
    def get_controlateral_columns(self):
        return {"time": ["timestamp", "Timestamp"], "dose_rate": ["dose_rate"]}

    # solo injection
    def load_data(self, inj_path, con_path=None):
        df_inj = self.data_manager.load_and_clean_data(inj_path, self.get_injection_columns())
        return df_inj, pd.DataFrame()

    # nessuna sincro con controlaterale: allinea su injection e duplica come dummy
    def synchronize_and_align(self, df_inj, df_con, base_name):
        dm = self.data_manager
        inj_aligned, _ = dm.align_with_injection_reference(df_inj, df_inj, total_minutes=15)
        return inj_aligned, inj_aligned.copy()

    def analyze_peak(self, df_inj, _df_con_not_used):
        """
        Analisi injection-only con la STESSA logica della diagnostica:
        - start su slope, picco ≤120 s
        - finestra fino a peak_time + WINDOW_AFTER_PEAK_S
        - plateau: derivata < 2 %·peak/s per ≥ 30 s
        """
        from analysis.diagnostic_analysis import analyze_injection_like_diagnostic

        if df_inj.empty:
            return pd.DataFrame(), pd.DataFrame(), {}

        df_inj_f, stats, _meta = analyze_injection_like_diagnostic(
            df_inj, dose_col="dose_rate", time_col="time_seconds"
        )
        if df_inj_f.empty:
            print("Curve a fondo – inj_only – skip")
            return pd.DataFrame(), pd.DataFrame(), {}

        self.last_stats = stats
        # ritorna un dummy 'con' non vuoto per compatibilità con BaseAnalysis
        return df_inj_f, df_inj_f.copy(), stats

    def plot_results(self, base_name, df_inj, _df_con, df_inj_filtered, _df_con_filtered):
        from plot_manager import plot_single_injection, plot_single_injection_normalized
        from config import PATH_GRAFICI_DIAGNOSTIC
        # fallback sicuro se alcune costanti non sono in config.py
        try:
            import config as cfg
            common_ylim = getattr(cfg, "INJ_ONLY_COMMON_YLIM", None)
            make_norm   = getattr(cfg, "INJ_ONLY_PLOT_NORMALIZED", True)
            sub_plot    = getattr(cfg, "INJ_ONLY_SUBDIR_PLOT", "plot")
            sub_norm    = getattr(cfg, "INJ_ONLY_SUBDIR_NORM", "normalized_plot")
        except Exception:
            common_ylim, make_norm, sub_plot, sub_norm = None, True, "plot", "normalized_plot"

        stats = getattr(self, "last_stats", None)

        # 1) Grafico assoluto (log) con unità e sottocartella dedicata
        plot_single_injection(
            base_name=f"{base_name}_injonly",
            df=df_inj_filtered,
            output_dir_base=PATH_GRAFICI_DIAGNOSTIC,
            yscale="log",
            dose_column="dose_rate",
            time_column="time_seconds",
            stats=stats,
            common_ylim=common_ylim,
            y_label="Dose rate [µSv/h]",
            subdir_name=sub_plot
        )

        # 2) Grafico normalizzato (0–1) in sottocartella dedicata
        if make_norm:
            plot_single_injection_normalized(
                base_name=f"{base_name}_injonly",
                df=df_inj_filtered,
                output_dir_base=PATH_GRAFICI_DIAGNOSTIC,
                dose_column="dose_rate",
                time_column="time_seconds",
                stats=stats,
                subdir_name=sub_norm
            )
