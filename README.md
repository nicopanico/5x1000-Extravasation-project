# 📊 Analisi Dati per Terapia e Diagnostica

Questo repository contiene un insieme di script Python per l'analisi dei dati relativi a terapie e acquisizioni diagnostiche.  
Il progetto è stato sviluppato per confrontare i dati di **injection** e **controlateral** provenienti da dosimetri (o sistemi analoghi) e per calcolare statistiche e metriche aggiuntive utili a:

- ✅ **Identificare casi di stravaso** (quando l’andamento della dose nel braccio di injection risulta anomalo).
- 📈 **Caratterizzare e confrontare l’andamento delle terapie o delle acquisizioni diagnostiche**.

---

## 🔹 Sommario

- [Overview](#-overview)
- [Requisiti](#-requisiti)
- [Struttura del Progetto](#-struttura-del-progetto)
- [Installazione](#-installazione)
- [Configurazione](#-configurazione)
- [Modalità di Esecuzione](#-modalità-di-esecuzione)
- [Metriche Calcolate](#-metriche-calcolate)
- [Output Generati](#-output-generati)
- [Come Usare ed Estendere il Codice](#-come-usare-ed-estendere-il-codice)


---

## 🔍 Overview

Il software esegue i seguenti step:

### 📥 1️⃣ Caricamento e Pulizia dei Dati
✔️ Lettura dei file **CSV** (gestione di separatori decimali, spazi extra, colonne duplicate).  
✔️ Conversione dei **timestamp** in formato datetime.  
✔️ Sincronizzazione tra **injection** e **controlateral**.  

### ⏳ 2️⃣ Sincronizzazione e Allineamento
✔️ Sincronizzazione dei dati tra **injection** e **controlateral** (con eventuali correzioni di shift temporali).  
✔️ Allineamento su una **griglia temporale regolare** (1 secondo di step).  

### 📊 3️⃣ Analisi del Picco
✔️ Calcolo del **picco** (tempo e valore).  
✔️ Identificazione del **tempo al plateau** (90% del valore stabile).  
✔️ Calcolo di **metriche aggiuntive** per la diagnosi o la terapia.  

### 📈 4️⃣ Calcolo di Metriche Aggiuntive
- Per **terapia** (tempo al 90%, AUC-delta, slope iniziale, ratio a intervalli...).
- Per **diagnostica** (colonne normalizzate, calcolo di picchi e plateau su *dose_rate*).

### 📉 5️⃣ Plot dei Risultati
✔️ Grafici annotati con curve di **injection** e **controlateral**.  
✔️ **Annotazioni per t₉₀, slope, ratio, ecc.**.  

### 💾 6️⃣ Salvataggio dei Risultati in Excel
✔️ Creazione del file **risultati_finali.xlsx**.  
✔️ Salvataggio di tre fogli Excel: **Stats**, **Delta**, **Ratio**.  

---

## 📋 Requisiti

✔ **Python 3.7+**  
✔ **Librerie richieste:**  

```bash
pandas
numpy
matplotlib
scipy
xlsxwriter  # (oppure openpyxl)
argparse
ABC
```

---

## 📂 Struttura del Progetto

```bash
ProjectRoot/
├── code/
│   ├── config.py
│   ├── data_manager.py
│   ├── main.py
│   ├── peak_analysis.py
│   ├── delta_analysis.py
│   ├── additional_metrics.py
│   ├── plot_manager.py
│   └── analysis/
│       ├── __init__.py
│       ├── base_analysis.py
│       ├── therapy_analysis.py
│       └── diagnostic_analysis.py
├── injections/              # CSV per la terapia
├── controlaterals/          # CSV per la terapia
└── stravaso_processed/      # CSV per la diagnostica
    ├── injections/
    └── controlaterals/
```

---

## 📊 Metriche Calcolate

Il software calcola diverse **metriche chiave** per valutare il comportamento della dose registrata nel tempo. Queste metriche aiutano sia a **identificare lo stravaso** sia a **caratterizzare il comportamento della terapia o della diagnostica**.

### 🔹 **Metriche per Terapia**
- **Picco della dose** (`peak_inj_time_s`, `peak_inj_value`, `peak_con_time_s`, `peak_con_value`)
- **Media dei dati filtrati** (`mean_inj_filtered`, `mean_con_filtered`)
- **Tempo al 90% della saturazione** (`time_to_90pct_inj`, `time_to_90pct_con`)
- **Slope iniziale** (`slope_inj_0_120s`)
- **Area sotto la curva (AUC-delta)** (`AUC_delta`)
- **Rapporto tra injection e controlateral (Ratio)**  
  - `ratio_60s`, `ratio_120s`, ..., `ratio_900s` (ogni 60s fino a 15 minuti)
  - `ratio_intervals_mean`
  - `ratio_max`

### 🔹 **Metriche per Diagnostica**
- **Picco della dose** (`peak_inj_time_s`, `peak_inj_value`)
- **Tempo al 90% della dose massima** (`time_to_plateau_inj`, `time_to_plateau_con`)
- **Slope iniziale** (`slope_rising`)
- **Area sotto la curva** (`area_after_peak`)

---
## ⚙️ CONFIGURAZIONE

Il file di configurazione principale del progetto è `config.py`.  
Qui vengono definiti i **percorsi dei dati**, le **modalità di analisi**, e le **colonne di interesse** per le due modalità di esecuzione: **terapia** e **diagnostica**.

### 📂 Percorsi dei Dati  

I dati vengono caricati da file **CSV** situati in directory specifiche.  
I percorsi sono definiti in `config.py`:

- **Terapia**  
  ```python
  ROOT_INJECTIONS_THERAPY = "percorso/cartella/injections"
  ROOT_CONTROLATERALS_THERAPY = "percorso/cartella/controlaterals"
  ```

- **Diagnostica**  
  ```python
  ROOT_INJECTIONS_DIAGNOSTIC = "percorso/cartella/stravaso_processed/injections"
  ROOT_CONTROLATERALS_DIAGNOSTIC = "percorso/cartella/stravaso_processed/controlaterals"
  ```

⚠️ **Importante:** Questi percorsi sono presi in automatico dallo script, è sufficiente che lo schema delle cartelle del tuo progetto sia come indicato nella sezione [#struttura-del-progetto].

### 📊 Directory di Output  

I grafici vengono salvati nelle seguenti directory:

- **Terapia**  
  ```python
  PATH_GRAFICI_THERAPY = "percorso/cartella/grafici"
  ```
- **Diagnostica**  
  ```python
  PATH_GRAFICI_DIAGNOSTIC = "percorso/cartella/stravaso_processed/grafici"
  ```
---
⚠️ **Importante:** Le cartelle "grafici" vengono create se non esistenti all'interno delle due cartelle apposite

## 📊 Output Generati

1. **Grafici Annotati**  
   - Curve di injection e controlateral.  
   - Annotazioni per tempi al 90%, slope, ratio, ecc.  
   - Salvati nella directory definita in `config.py`.

2. **File Excel `risultati_finali.xlsx`**  
   - Creato nella stessa cartella dei grafici.  
   - Contiene tre fogli principali:
     - **Stats**: statistiche generali.  
     - **Delta**: delta calcolati a determinati time-point.  
     - **Ratio**: metriche relative ai rapporti.

---

## 🛠️ Come Usare ed Estendere il Codice

### Configurazione:
- Modifica `config.py` per impostare i percorsi dei dati e la modalità di analisi.

### Esecuzione:
```bash
python main.py --mode therapy
```
oppure
```bash
python main.py --mode diagnostic
```

### Estensione:
- Il progetto utilizza una classe base `BaseAnalysis` per definire il flusso di lavoro.
- Le classi `TherapyAnalysis` e `DiagnosticAnalysis` implementano la logica specifica per ciascuna modalità.
- Per aggiungere nuove metriche, puoi modificare `analyze_peak`, `compute_therapy_metrics` o `compute_diagnostic_metrics`.

---





