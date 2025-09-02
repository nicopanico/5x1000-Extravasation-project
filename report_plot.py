# reporting.py (bozza)
import os, numpy as np, pandas as pd
import matplotlib.pyplot as plt

def load_stats(path_excel, sheet="Stats", label_col=None):
    df = pd.read_excel(path_excel, sheet_name=sheet)
    if label_col and label_col in df.columns:
        df["severe"] = df[label_col].astype(int)
    return df

def dist_ratio_dose(df, outdir):
    os.makedirs(outdir, exist_ok=True)
    plt.figure(figsize=(8,5))
    if "severe" in df.columns:
        for lab, g in df.groupby("severe"):
            plt.hist(g["ratio_dose"].clip(-0.2,1.0), bins=30, alpha=0.5, label=f"severe={lab}")
        plt.legend()
    else:
        plt.hist(df["ratio_dose"].clip(-0.2,1.0), bins=30, alpha=0.7)
    plt.xlabel("ratio_dose [1]"); plt.ylabel("count")
    plt.title("Distribuzione di ratio_dose")
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(outdir,"dist_ratio_dose.png"), bbox_inches="tight"); plt.close()

def scatter_ratio_delta(df, outdir):
    os.makedirs(outdir, exist_ok=True)
    plt.figure(figsize=(7,6))
    if "severe" in df.columns:
        for lab, g in df.groupby("severe"):
            plt.scatter(g["ratio_dose"], g["delta_dose"], alpha=0.7, label=f"severe={lab}")
        plt.legend()
    else:
        plt.scatter(df["ratio_dose"], df["delta_dose"], alpha=0.7)
    plt.xlabel("ratio_dose [1]"); plt.ylabel("delta_dose [µSv/h]")
    plt.title("ratio_dose vs delta_dose"); plt.grid(alpha=0.3)
    plt.savefig(os.path.join(outdir,"scatter_ratio_delta.png"), bbox_inches="tight"); plt.close()

def agreement_injonly_vs_diag(df_inj, df_diag, outdir, key="base_name"):
    os.makedirs(outdir, exist_ok=True)
    m = pd.merge(df_inj[[key,"ratio_dose"]], df_diag[[key,"ratio_dose"]], on=key, suffixes=("_inj","_diag"))
    r = m[["ratio_dose_inj","ratio_dose_diag"]].corr().iloc[0,1]
    plt.figure(figsize=(6,6))
    plt.scatter(m["ratio_dose_inj"], m["ratio_dose_diag"], alpha=0.7)
    lim = [min(m.min().min(),0), max(m.max().max(),1)]
    plt.plot(lim, lim, "k--", lw=1)
    plt.xlim(lim); plt.ylim(lim)
    plt.xlabel("inj_only ratio_dose [1]"); plt.ylabel("diagnostic ratio_dose [1]")
    plt.title(f"Concordanza inj_only vs diagnostic (r={r:.3f})")
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(outdir,"agreement_ratio_dose.png"), bbox_inches="tight"); plt.close()
    return r, m
