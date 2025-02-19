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

Il software calcola diverse **metriche chiave** per valutare l’andamento della dose/dose rate registrata nel tempo, sia per **terapia** sia per **diagnostica**. Queste metriche aiutano a:

1. **Identificare** eventuali anomalie (es. stravaso o curve “insolite”).  
2. **Caratterizzare** in modo quantitativo la curva di dose/dose rate (valori massimi, velocità di salita, area residua…).

### 🔹 Struttura di Base delle Metriche

1. **Peak Analysis** (tempo e valore del picco)  
2. **Tempo al plateau** (rapido raggiungimento di una soglia% del picco)  
3. **Media e Max** su injection e controlateral (dose o dose rate)  
4. **Delta** injection–controlateral a tempo variabile  
5. **Metriche aggiuntive** (area dopo picco, slope iniziale, etc.)

#### Peak Analysis

- **peak_inj_time_s / peak_inj_value**: tempo e valore del picco nel dataset injection.  
- **peak_con_time_s / peak_con_value**: tempo e valore del picco nel dataset controlateral.  
  - *Interpretazione*: indica **quando** (in secondi) si verifica il valore massimo della curva e **qual è** quell’intensità (dose, dose rate, ecc.). Un picco molto alto può segnalare un’intensità raggiunta improvvisamente.

#### Mean e Max

- **mean_inj_filtered / mean_con_filtered**: media (filtrata) rispettivamente su injection e controlateral.  
- **max_inj / max_con**: calcola i massimi (eventualmente senza filtraggio) per injection e controlateral.  
  - *Interpretazione*: fornisce **il livello medio** e **il valore massimo** della curva, aiutando a capire la “forza” globale del segnale sul lato injection vs. controlateral.

#### Tempo al Plateau

- **time_to_plateau_inj / time_to_plateau_con**: primo istante in cui la curva injection (o controlateral) supera una certa soglia (ad es. 85% o 90%) del picco.  
  - *Interpretazione*: **quanto velocemente** la curva raggiunge (o quasi) il suo massimo. Un tempo al plateau più breve indica un aumento rapido della dose/dose rate.

#### Delta Analysis

- **\(\Delta(t)\) = |inj(t) − con(t)|**: differenza assoluta tra injection e controlateral in vari time-point.  
- **mean_delta**: media delle differenze \(\Delta\).  
  - *Interpretazione*: valuta **quanto** i due lati (injection vs. controlateral) divergono nel tempo. Un \(\Delta\) elevato segnala un’**asimmetria** marcata fra i due bracci.

#### Metriche Aggiuntive

- **area_after_peak**: integrale della curva dal picco fino al termine.  
  - *Interpretazione*: quantifica **quanta** dose/dose rate rimane **dopo** il picco; utile per analizzare la coda del fenomeno (fase discendente).  
- **slope_rising**: pendenza tra l’inizio del tracciato e il picco.  
  - *Interpretazione*: indica **la velocità di salita** della curva: se il segnale sale velocemente, la pendenza è alta.  
- **delta_dose** = (peak_value − mean_value): differenza assoluta tra picco e media.  
  - *Interpretazione*: quanto il picco supera mediamente la curva, in valore assoluto.  
- **ratio_dose** = (peak_value − mean_value) / peak_value: differenza (picco − media) normalizzata sul picco.  
  - *Interpretazione*: esprime **in forma percentuale** quanto la media si discosta dal picco; un valore vicino a 1 indica che la media è molto inferiore al picco.

---

### 🔹 Esempi di Significato Fisico

- **Picco** (peak_inj_value, peak_inj_time_s): massimo tasso di dose (dose rate) → *punto di maggiore intensità* nel braccio di iniezione.  
- **Tempo al plateau**: *velocità di reazione del sistema*, quanto tempo serve a raggiungere l’85–90% del valore di picco.  
- **Area dopo il picco** (area_after_peak): *dose residua* o *quantità integrata* accumulata nella fase discendente.  
- **Slope iniziale** (slope_rising): *rapidità con cui la dose cresce* dall’inizio fino al picco.  
- **Delta** injection–controlateral: *differenza tra i due bracci*, potenzialmente utile per evidenziare stravaso (lato injection) se la curva si discosta molto dal controlateral.  

Con queste metriche, il software fornisce un **quadro completo** dell’andamento temporale di dose/dose rate e rende possibile il **confronto** tra i due lati (injection vs. controlateral) e/o tra diverse acquisizioni.

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

⚠️ **Importante:** Questi percorsi sono presi in automatico dallo script, è sufficiente che lo schema delle cartelle del tuo progetto sia come indicato nella sezione [Struttura del Progetto](#-struttura-del-progetto).

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





