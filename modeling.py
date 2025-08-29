# modeling.py
import pandas as pd
import numpy as np

def _fbeta_at_threshold(y_true, y_prob, thr, beta=2.0):
    y_pred = (y_prob >= thr).astype(int)
    tp = ((y_true==1) & (y_pred==1)).sum()
    fp = ((y_true==0) & (y_pred==1)).sum()
    fn = ((y_true==1) & (y_pred==0)).sum()
    precision = tp / (tp + fp) if (tp+fp) else 0.0
    recall = tp / (tp + fn) if (tp+fn) else 0.0
    if precision==0 and recall==0:
        return 0.0, precision, recall
    beta2 = beta**2
    fbeta = (1+beta2) * (precision*recall) / (beta2*precision + recall) if (precision+recall)>0 else 0.0
    return fbeta, precision, recall

def suggest_threshold_by_fbeta(y_true, y_score, beta=2.0, grid=None):
    if grid is None:
        grid = np.linspace(0.0, 1.0, 501)
    best = (-1, 0.5, 0.0, 0.0)  # fbeta, thr, prec, rec
    for thr in grid:
        f, p, r = _fbeta_at_threshold(y_true, y_score, thr, beta=beta)
        if f > best[0]:
            best = (f, thr, p, r)
    return {"beta": beta, "fbeta": best[0], "threshold": best[1], "precision": best[2], "recall": best[3]}

def fit_model_from_excel(path_excel, sheet="Stats", label_col="severe",
                         feature_cols=("ratio_dose","delta_dose","area_after_peak","slope_rising"),
                         beta=2.0):
    """
    path_excel: tuo excel con i casi 'grossi' (label_col=1) e i casi normali (0)
    Ritorna: dizionario con coeff, soglia F-beta e utilità cliniche.
    """
    df = pd.read_excel(path_excel, sheet_name=sheet)
    df = df.dropna(subset=[label_col]).copy()
    # pulizia features
    X = df.loc[:, feature_cols].astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0).values
    y = df[label_col].astype(int).values

    # prova sklearn, fallback su una regola 1D (ratio_dose)
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
        from sklearn.metrics import average_precision_score

        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=200, class_weight={0:1, 1:2}))  # più peso ai positivi
        ])
        pipe.fit(X, y)
        y_score = pipe.predict_proba(X)[:,1]
        ap = average_precision_score(y, y_score)
        fbeta_res = suggest_threshold_by_fbeta(y, y_score, beta=beta)

        return {
            "model": pipe,
            "features": feature_cols,
            "average_precision": float(ap),
            "fbeta": fbeta_res,
        }
    except Exception as e:
        # fallback: solo ratio_dose con soglia
        ratio = df["ratio_dose"].astype(float).values
        # severi attesi con ratio basso → invertiamo per avere score alto=severo
        y_score = 1.0 - np.clip(ratio, 0, 1)
        fbeta_res = suggest_threshold_by_fbeta(y, y_score, beta=beta)
        return {
            "model": None,
            "features": ("ratio_dose",),
            "note": f"fallback rule-based (no sklearn): {e}",
            "fbeta": fbeta_res
        }
