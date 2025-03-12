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
├── Terapia/
│   ├── injections/              # CSV per la terapia (iniezione)
│   ├── controlaterals/          # CSV per la terapia (controlaterale)
│   └── grafici/                 # Grafici e risultati (terapia)
├── Diagnostica/
│   └── stravaso_processed/
│       ├── injections/          # CSV per la diagnostica (iniezione)
│       ├── controlaterals/      # CSV per la diagnostica (controlaterale)
│       └── grafici/             # Grafici e risultati (diagnostica)
└── README.md

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

### 🔹 Metriche per la **Terapia**

Nella classe `TherapyAnalysis`, oltre a calcolare i parametri comuni (peak analysis, media filtrata, ecc.), vengono introdotte alcune metriche specifiche per valutare l’andamento della **dose rate** nel contesto terapeutico:

1. **Tempo al 90% del plateau** (`time_to_90pct_inj` e `time_to_90pct_con`)
   - Dopo aver definito il "plateau" come la **media** degli ultimi 120 secondi della curva, si calcola il 90% di tale valore e si cerca **quando** la curva lo raggiunge. Oppure la media dei 100 secondi dopo il picco. 
   - **Significato**: indica **quanto rapidamente** injection (o controlateral) arriva alla soglia “quasi-stazionaria” (90% del plateau). Un valore più basso suggerisce che la curva sale velocemente e si stabilizza.

2. **AUC-delta** (`AUC_delta`)
   - Differenza tra injection e controlateral (`inj - con`), integrata rispetto al tempo (metodo del trapezio).  
   - **Significato**: stima **quanto** la dose rate del braccio injection **eccede** (o difetta, se negativo) rispetto al controlateral **nell’intero arco temporale** (fino a 15 minuti). Un valore elevato potrebbe segnalare un grande scostamento “cumulato” tra i due lati (es. potenziale stravaso).

3. **Slope iniziale Injection (0–120 s)** (`slope_inj_0_120s`)
   - Pendenza del segnale injection calcolata tra 0 e 120 secondi.  
   - **Significato**: misura la **rapidità di salita iniziale** del dose rate nel braccio iniettato; se il segnale cresce molto velocemente, lo slope è alto. È utile per capire se la sostanza si distribuisce rapidamente.

4. **Metriche di Rapporto Injection–Controlateral** (dizionario `ratio_stats`)
   - Calcola la serie `ratio_series = inj / con` (dose rate injection diviso controllo), e ne estrapola:
     - `ratio_{t}s` ogni 60 secondi (fino a 15 minuti): es. `ratio_60s`, `ratio_120s`, …  
     - `ratio_intervals_mean`: media dei rapporti a questi time-point.  
     - `ratio_max`: massimo della serie `inj / con` su tutto l’intervallo.  
     - `ratio_mean`: media globale dell’intero rapporto su injection e controlateral (no time-point specifici).  
   - **Significato**: confronta i valori di dose rate su injection e controlateral lungo l’intero arco di 15 minuti, sia in punti fissi (ogni 60s) sia globalmente. Un rapporto molto alto indica che il braccio injection ha dose rate marcatamente maggiore rispetto al controlateral (possibile segno di accumulo anomalo).

---

**In sintesi**, l’analisi per la terapia si focalizza su:

- **Quanto** e **come** la curva injection supera (o si differenzia da) la curva controlateral (AUC-delta, ratio).  
- **Quando** la curva raggiunge una soglia di “stabilità” (tempo al 90%).  
- **Con che velocità** sale inizialmente (slope 0–120s).  

Tali informazioni aiutano a **verificare** se la dose si distribuisce in modo normale (controlateral simile a injection, ratio moderato) o se ci sono anomalie (ratio alto, AUC-delta elevata, slope molto ripido, etc.). 

### 🔹 Metriche per la **Diagnostica**

Nell’analisi **diagnostica**, il codice si concentra soprattutto su variabili di **dose rate** (μSv/h) per un intervallo più breve (ad esempio 10 minuti) e calcola metriche incentrate su **picco** e **rapidità** dell’andamento:

1. **Tempo al Plateau** (`time_to_plateau_inj` e `time_to_plateau_con`)  
   - Ricerca dell’istante in cui injection (o controlateral) raggiunge l’85–90% del proprio picco.  
   - **Significato**: quantifica **quanto velocemente** la curva sale quasi al massimo. Un tempo al plateau minore indica un’ascesa rapida della dose rate.

2. **Slope Iniziale** (`slope_rising`)  
   - Pendenza (o “speed of rise”) dalla prima misurazione fino al tempo di picco.  
   - **Significato**: valuta **la velocità** con cui il segnale (dose rate) cresce inizialmente. Un valore elevato suggerisce un’immissione o diffusione rapida del radiofarmaco.

3. **Area dopo il Picco** (`area_after_peak`)  
   - Integrale della curva dal picco fino al termine dell’intervallo (ad es. 10 minuti).  
   - **Significato**: misura la **quantità di dose “residua”** nella fase discendente della curva, utile a stimare se c’è una coda significativa dopo aver raggiunto il massimo.

4. **Delta Dose** e **Ratio Dose** (`delta_dose`, `ratio_dose`)  
   - **delta_dose** = (peak_value − mean_value)  
   - **ratio_dose** = (peak_value − mean_value) / peak_value  
   - **Significato**: indicano **quanto** (in valore assoluto o in termini percentuali) il picco eccede la media del segnale. Un alto `delta_dose` suggerisce un picco molto pronunciato, mentre `ratio_dose` > 0.8 (ad es.) significherebbe che la media sta ben sotto il picco.

---

**In sintesi**, nell’analisi diagnostica si enfatizzano:

- **Il picco** (max dose rate), **quanto velocemente** lo si raggiunge (tempo al plateau, slope).  
- **Quanta coda** c’è nella fase discendente (area_after_peak).  
- **Quanto** il picco eccede la media (delta_dose, ratio_dose).  

Questo permette di **caratterizzare** una curva di dose rate in modo approfondito, fornendo parametri utili a valutazioni cliniche o di processo (se la dose in un certo distretto corporeo sale rapidamente e si mantiene, o se c’è un picco molto breve e poi un rapido calo, ecc.). 

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





