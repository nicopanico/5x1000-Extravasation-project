# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 16:10:43 2025

@author: nicop
"""

import os
import pandas as pd
from datetime import datetime


## 1__
class DataManager:
    def __init__(self, root_injection, root_controlateral):
        self.root_injection = root_injection
        self.root_controlateral = root_controlateral

    def get_file_names(self):
        """
        Cerca i file CSV nelle cartelle injection/ e controlaterals/
        che hanno lo stesso 'nome base', dove:
          - Nella cartella injection i file si chiamano ..._inj.csv
          - Nella cartella controlaterals i file si chiamano ..._cont.csv

        Restituisce una lista di questi ID (nome base).
        Esempio: 
          se c'è un file "D223512_2025_03_21_inj.csv" in injection e 
              un file "D223512_2025_03_21_cont.csv" in controlaterals,
          allora genera un id = "D223512_2025_03_21".
        """
        from config import ANALYSIS_MODE
        mode = ANALYSIS_MODE.lower()

        suffix_inj  = "_inj.csv"
        suffix_cont = "_cont.csv"

        inj_files = [f for f in os.listdir(self.root_injection) if f.endswith(suffix_inj)]

        if mode == "inj_only":
            # es. "pipopo_tre_inj.csv" -> "pipopo_tre"
            return sorted({f[:-len(suffix_inj)] for f in inj_files})

        # modalità classiche: richiedi anche il controlaterale
        con_files = [f for f in os.listdir(self.root_controlateral) if f.endswith(suffix_cont)]
        inj_bases = {f[:-len(suffix_inj)] for f in inj_files}
        con_bases = {f[:-len(suffix_cont)] for f in con_files}
        return sorted(inj_bases.intersection(con_bases))

    
    @staticmethod
    def _first_present(df_cols, aliases):
        """
        Restituisce il primo alias presente fra le colonne, ignorando maiuscole/minuscole.
        """
        if isinstance(aliases, str):
            aliases = [aliases]

        # mappa lowercase → nome originale
        lc_map = {c.lower(): c for c in df_cols}

        for a in aliases:
            key = a.lower()
            if key in lc_map:
                return lc_map[key]  # restituisce il nome esatto presente nel DF
        return None
    def load_and_clean_data(self, path, columns_of_interest=None,
                            sep=",", encoding="utf-8"):
        """
        Lettura CSV robusta e normalizzazione nomi-colonna.
        - normalizza header: minuscole, trim, µ/μ -> 'u'
        - parsing timestamp robusto (ISO, dayfirst, formati espliciti, fallback secondi)
        - coercizione numerica di dose_rate / intensity (virgola o punto)
        - scelta 'dose_rate' come vera serie temporale
        - normalizzazione unità (nSv/h -> µSv/h; mSv/h -> µSv/h) se disponibile
        """
        import pandas as pd
        from config import ANALYSIS_MODE
        import os

        # ---------- util ----------
        def _normalize_headers(cols):
            out = []
            for c in cols:
                s = str(c).strip()
                s = s.replace("µ", "u").replace("μ", "u")  # micro -> 'u'
                s = s.lower()
                s = " ".join(s.split())                   # spazi multipli -> uno
                out.append(s)
            return out

        def _to_float(series: pd.Series) -> pd.Series:
            # gestisce sia virgola che punto come separatore decimale + spazi
            if series.dtype.kind in "biufc":
                return pd.to_numeric(series, errors="coerce")
            s = series.astype(str).str.strip().str.replace(" ", "", regex=False)
            s = s.str.replace(",", ".", regex=False)
            return pd.to_numeric(s, errors="coerce")

        def _read_flex(p, enc_primary="utf-8"):
            # prova (utf-8, ","), (utf-8, ";"), poi (cp1252, ","), (cp1252, ";")
            for enc_try in (enc_primary, "cp1252"):
                for sep_try in (",", ";"):
                    try:
                        df = pd.read_csv(p, sep=sep_try, encoding=enc_try,
                                         engine="python", on_bad_lines="skip")
                        if df.shape[1] > 1:
                            return df, sep_try, enc_try
                    except Exception:
                        continue
            raise IOError("Impossibile leggere CSV con encoding/sep noti")

        # ---------- 1) Lettura CSV (sep + encoding robusti) ----------
        try:
            df_raw, used_sep, used_enc = _read_flex(path, enc_primary=encoding)
            # print(f"[Read] {os.path.basename(path)} sep={used_sep} enc={used_enc}")
        except Exception as e:
            print(f"Errore lettura '{path}': {e}")
            return pd.DataFrame()

        # ---------- 2) Header normalizzati ----------
        df_raw.columns = _normalize_headers(df_raw.columns)
        if df_raw.columns.duplicated().any():
            df_raw = df_raw.loc[:, ~df_raw.columns.duplicated(keep="first")]

        mode = ANALYSIS_MODE.lower()

        # ---------- 3) Parsing TEMPO robusto ----------
        time_col = None
        if columns_of_interest and "time" in columns_of_interest:
            time_col = self._first_present(df_raw.columns, columns_of_interest["time"])
        if time_col is None:
            for cand in ("timestamp", "time", "date time", "date/time", "datetime", "data/ora", "record time"):
                if cand in df_raw.columns:
                    time_col = cand
                    break

        if time_col is not None:
            tseries = df_raw[time_col]

            # (1) generico (ISO, RFC, ecc.)
            t = pd.to_datetime(tseries, errors="coerce")

            # (2) se ancora tanti NaT, dayfirst + infer
            if t.isna().mean() > 0.5:
                t = pd.to_datetime(tseries, errors="coerce", dayfirst=True, infer_datetime_format=True)

            # (3) se ancora tanti NaT, formati espliciti (incl. anno 2 cifre)
            if t.isna().mean() > 0.5:
                for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%y %H:%M:%S",
                            "%d-%m-%Y %H:%M:%S", "%d-%m-%y %H:%M:%S"):
                    tt = pd.to_datetime(tseries, errors="coerce", dayfirst=True, format=fmt)
                    if tt.isna().mean() < t.isna().mean():
                        t = tt
                    if t.isna().mean() < 0.5:
                        break

            # (4) fallback: seconds numerici
            if t.isna().mean() > 0.5:
                sec = pd.to_numeric(tseries, errors="coerce")
                if sec.notna().mean() > 0.5:
                    base = pd.Timestamp("1970-01-01")
                    t = base + pd.to_timedelta(sec, unit="s")

            df_raw["time"] = t
            if t.notna().any():
                df_raw.set_index("time", drop=False, inplace=True)
                df_raw.sort_index(inplace=True)
                df_raw = df_raw[~df_raw.index.duplicated(keep="first")]

        # ---------- 4) Estrazione colonne di interesse ----------
        if columns_of_interest:
            # helper: scegli una colonna "serie temporale" tra gli alias
            def _pick_timeseries_col(df, aliases, avoid_tokens=("max",)):
                aliases_lc = [a.lower() for a in (aliases if isinstance(aliases, (list, tuple)) else [aliases])]

                # candidati presenti nel DF
                cands = [c for c in df.columns if c.lower() in aliases_lc]
                if not cands:
                    return None

                # 1) elimina candidati con token da evitare (es. "max")
                def _bad(lc_name: str) -> bool:
                    return any(tok in lc_name for tok in avoid_tokens)

                good = [c for c in cands if not _bad(c.lower())]
                pool = good if good else cands  # se tutti "cattivi", usa comunque qualcosa

                # 2) preferisci nomi 'sicuri' (dose_rate, intensità di dose)
                def _priority(name: str) -> int:
                    n = name.lower()
                    if "dose_rate" in n or "dose rate" in n:
                        return 0
                    if "intensita" in n or "intensità" in n:
                        return 1
                    return 2

                pool.sort(key=_priority)

                # 3) tra i rimanenti, scegli quello con più valori distinti (su numerico!)
                best, best_uniques = None, -1
                for c in pool:
                    nun = _to_float(df[c]).dropna().nunique()  # <-- numerico, non stringhe
                    if nun > best_uniques:
                        best_uniques, best = nun, c
                return best

            extracted = {}
            for key, aliases in columns_of_interest.items():
                if key in ("dose_rate", "intensity"):
                    col = _pick_timeseries_col(df_raw, aliases)
                else:
                    col = self._first_present(df_raw.columns, aliases)

                if col:
                    extracted[key] = df_raw[col]
                else:
                    print(f"[Warn] colonna '{key}' non trovata – alias {aliases}")

            df_clean = pd.DataFrame(extracted)

            # --- Coercizione numerica ---
            for num_key in ("dose_rate", "intensity", "dose", "count_rate"):
                if num_key in df_clean.columns:
                    df_clean[num_key] = _to_float(df_clean[num_key])

            # --- Normalizzazione unità se presente una colonna 'unit' ---
            # es. 'dose rate unit' | 'dose_rate_unit' | 'unit' | 'dose unit'
            unit_col = None
            for cand in ("dose rate unit", "dose_rate_unit", "unit", "dose unit"):
                if cand in df_raw.columns:
                    unit_col = cand
                    break
            if unit_col and "dose_rate" in df_clean.columns:
                u0 = str(df_raw[unit_col].iloc[0]).strip().lower()
                if "nsv" in u0:      # nanoSv/h -> microSv/h
                    df_clean["dose_rate"] = df_clean["dose_rate"] / 1000.0
                elif "msv" in u0:    # milliSv/h -> microSv/h
                    df_clean["dose_rate"] = df_clean["dose_rate"] * 1000.0
                # 'usv'/'µsv' già in µSv/h → nessuna azione

            # --- tempo in datetime se non lo è già ---
            if "time" in df_clean.columns and not pd.api.types.is_datetime64_any_dtype(df_clean["time"]):
                df_clean["time"] = pd.to_datetime(df_clean["time"], errors="coerce")

            # ---------- 5) Drop NaN sulla colonna essenziale + warning variabilità ----------
            if mode in ("diagnostic", "inj_only"):
                essential_alias = columns_of_interest.get("dose_rate", ["dose_rate"])
                ess_col = self._first_present(df_clean.columns, essential_alias)
                if ess_col:
                    if df_clean[ess_col].dropna().nunique() < 10:
                        print(f"[Warn] '{ess_col}' ha pochi valori distinti: possibile colonna non temporale.")
                    df_clean.dropna(subset=[ess_col], inplace=True)
            else:  # therapy
                essential_alias = columns_of_interest.get("intensity", ["intensità di dose (usv/h)"])
                ess_col = self._first_present(df_clean.columns, essential_alias)
                if ess_col:
                    df_clean.dropna(subset=[ess_col], inplace=True)

            # log di debug minimale (commenta se non serve)
            mapped = ", ".join(f"{k}->{v.name if hasattr(v,'name') else v}" for k,v in df_clean.items())
            print(f"[Map] {os.path.basename(path)} : {mapped}")

            return df_clean

        # Se non si chiede estrazione specifica: drop generico dei NaN
        df_raw.dropna(how="any", inplace=True)
        return df_raw

    #3__       
    def synchronize_data(self, df_inj: pd.DataFrame, df_con: pd.DataFrame, base_name: str):
        if df_inj.empty or df_con.empty:
            return df_inj, df_con
    
        # Estrai il primo timestamp da ciascun DataFrame
        start_inj = df_inj.index[0]
        start_con = df_con.index[0]
    
        # Se uno dei timestamp è NaT, stampare un messaggio e restituire DataFrame vuoti per segnalare che questo file va saltato
        if pd.isna(start_inj) or pd.isna(start_con):
            print(f"Attenzione: per il paziente {base_name} uno dei timestamp iniziali è NaT. Skip questo file.")
            return pd.DataFrame(), pd.DataFrame()
    
        # Calcola la differenza di tempo e procedi normalmente
        delta = abs(start_inj - start_con)
        minutes_diff = delta.total_seconds() / 60.0
    
        if minutes_diff > 50:
            if start_inj > start_con:
                df_inj.index = df_inj.index - pd.Timedelta(minutes=58.4)
            else:
                df_con.index = df_con.index - pd.Timedelta(minutes=58.4)
    
        if "20_03" in base_name or "23_03" in base_name:
            df_con.index = df_con.index + pd.Timedelta(minutes=3)
    
        return df_inj, df_con

    
    # 4_
    def get_paths_for_base(self, base_name):
        """
        Dato un nome base, restituisce i percorsi completi dei file di injection e controlateral.
        Si assume che:
          - Il file di injection si chiami "{base_name}_inj.csv"
          - Il file di controlateral si chiami "{base_name}_cont.csv"
        """
        inj_path = os.path.join(self.root_injection, f"{base_name}_inj.csv")
        con_path = os.path.join(self.root_controlateral, f"{base_name}_cont.csv")
        return inj_path, con_path
    
    def align_with_injection_reference(self, df_inj, df_con, total_minutes=15):
        if df_inj.empty or df_con.empty:
            return df_inj, df_con

        # Rimuovi duplicati nell'indice, se presenti
        df_inj = df_inj[~df_inj.index.duplicated(keep='first')]
        df_con = df_con[~df_con.index.duplicated(keep='first')]

        # Elimina eventuali duplicati del tempo come colonne ridondanti
        for col in ("timestamp", "Timestamp"):  # gestiti a livello DF normalizzato, ma per sicurezza
            if col in df_inj.columns:
                df_inj = df_inj.drop(columns=[col])
            if col in df_con.columns:
                df_con = df_con.drop(columns=[col])

        # --- Prova con datetime "reali" (indice datetime) ---
        inj_start_time = df_inj.index.min() if isinstance(df_inj.index, pd.DatetimeIndex) else pd.NaT
        inj_end_time = inj_start_time + pd.Timedelta(minutes=total_minutes) if pd.notna(inj_start_time) else pd.NaT

        if pd.notna(inj_start_time) and pd.notna(inj_end_time):
            # Range regolare a 1 Hz
            time_range = pd.date_range(start=inj_start_time, end=inj_end_time, freq='1s')

            df_inj_cut = df_inj.loc[(df_inj.index >= inj_start_time) & (df_inj.index <= inj_end_time)].copy()
            df_con_cut = df_con.loc[(df_con.index >= inj_start_time) & (df_con.index <= inj_end_time)].copy()

            df_inj_aligned = df_inj_cut.reindex(time_range).interpolate(method='linear')
            df_con_aligned = df_con_cut.reindex(time_range).interpolate(method='linear')

            df_inj_aligned['time_seconds'] = (df_inj_aligned.index - inj_start_time).total_seconds().astype(int)
            df_con_aligned['time_seconds'] = (df_con_aligned.index - inj_start_time).total_seconds().astype(int)

            df_inj_aligned['time'] = df_inj_aligned.index
            df_con_aligned['time'] = df_con_aligned.index

            df_inj_aligned.reset_index(drop=True, inplace=True)
            df_con_aligned.reset_index(drop=True, inplace=True)
            return df_inj_aligned, df_con_aligned

        # --- Fallback: asse a secondi (se timestamp NaT o indice non datetime) ---
        # usa 'time_seconds' se presente, altrimenti l’indice numerico come secondi a 1 Hz
        if "time_seconds" in df_inj.columns and pd.api.types.is_numeric_dtype(df_inj["time_seconds"]):
            inj_sec = pd.to_numeric(df_inj["time_seconds"], errors="coerce").fillna(method="ffill")
        else:
            inj_sec = pd.Series(range(len(df_inj)), index=df_inj.index)

        horizon = min(int(pd.to_numeric(inj_sec, errors="coerce").max()), int(total_minutes * 60))
        time_range_td = pd.timedelta_range(start="0s", end=f"{horizon}s", freq="1s")

        inj_idx = pd.to_timedelta(inj_sec, unit="s")
        df_inj_aligned = df_inj.set_index(inj_idx).reindex(time_range_td).interpolate()

        if not df_con.empty:
            if "time_seconds" in df_con.columns and pd.api.types.is_numeric_dtype(df_con["time_seconds"]):
                con_sec = pd.to_numeric(df_con["time_seconds"], errors="coerce").fillna(method="ffill")
            else:
                con_sec = pd.Series(range(len(df_con)), index=df_con.index)
            con_idx = pd.to_timedelta(con_sec, unit="s")
            df_con_aligned = df_con.set_index(con_idx).reindex(time_range_td).interpolate()
        else:
            df_con_aligned = df_inj_aligned.copy()

        base = pd.Timestamp("1970-01-01")
        df_inj_aligned["time"] = base + df_inj_aligned.index
        df_con_aligned["time"] = base + df_con_aligned.index
        df_inj_aligned["time_seconds"] = df_inj_aligned.index.total_seconds().astype(int)
        df_con_aligned["time_seconds"] = df_con_aligned.index.total_seconds().astype(int)

        df_inj_aligned.reset_index(drop=True, inplace=True)
        df_con_aligned.reset_index(drop=True, inplace=True)
        return df_inj_aligned, df_con_aligned

    def get_file_names_inj_only(self):
        inj_files = [f for f in os.listdir(self.root_injection) if f.endswith('_inj.csv')]
        return sorted({f.replace('_inj.csv', '') for f in inj_files})
