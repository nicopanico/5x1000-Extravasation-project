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

def curves_pr_roc(df, outdir, use_model_score=False):
    from sklearn.metrics import precision_recall_curve, average_precision_score, roc_curve, auc
    os.makedirs(outdir, exist_ok=True)
    y = df["severe"].astype(int).values
    score = df["score"].values if use_model_score else (1.0 - df["ratio_dose"].clip(0,1).values)

    # PR
    p, r, thr = precision_recall_curve(y, score)
    ap = average_precision_score(y, score)
    plt.figure(figsize=(6,5)); plt.plot(r, p); plt.xlabel("Recall"); plt.ylabel("Precision")
    plt.title(f"PR curve (AP={ap:.3f})"); plt.grid(alpha=0.3)
    plt.savefig(os.path.join(outdir,"pr_curve.png"), bbox_inches="tight"); plt.close()

    # ROC
    fpr, tpr, thr2 = roc_curve(y, score)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(6,5)); plt.plot(fpr, tpr); plt.plot([0,1],[0,1],"k--")
    plt.xlabel("FPR"); plt.ylabel("TPR"); plt.title(f"ROC (AUC={roc_auc:.3f})"); plt.grid(alpha=0.3)
    plt.savefig(os.path.join(outdir,"roc_curve.png"), bbox_inches="tight"); plt.close()

def confusion_at_threshold(df, thr, outdir, use_model_score=False):
    from sklearn.metrics import confusion_matrix
    os.makedirs(outdir, exist_ok=True)
    y = df["severe"].astype(int).values
    score = df["score"].values if use_model_score else (1.0 - df["ratio_dose"].clip(0,1).values)
    yhat = (score >= thr).astype(int)
    cm = confusion_matrix(y, yhat, labels=[0,1])  # [[TN,FP],[FN,TP]]
    tn, fp, fn, tp = cm.ravel()
    plt.figure(figsize=(4,4))
    plt.imshow(cm, cmap="Blues"); plt.xticks([0,1],["Pred 0","Pred 1"]); plt.yticks([0,1],["True 0","True 1"])
    for i,(r) in enumerate(cm):
        for j,v in enumerate(r):
            plt.text(j,i,str(v), ha="center", va="center")
    plt.title(f"Confusion (thr={thr:.2f})"); plt.colorbar()
    plt.savefig(os.path.join(outdir,"confusion.png"), bbox_inches="tight"); plt.close()
    return dict(tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp))
