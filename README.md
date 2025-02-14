# Analisi Dati per Terapia e Diagnostica

Questo repository contiene un insieme di script Python per l'analisi dei dati relativi a **terapie** e **acquisizioni diagnostiche**. Il progetto è stato sviluppato per confrontare i dati di **injection** e **controlateral** provenienti da dosimetri (o sistemi analoghi) e per calcolare statistiche e metriche aggiuntive utili a:

- Identificare casi di **stravaso** (quando l’andamento della dose nel braccio di injection risulta anomalo).
- Caratterizzare e confrontare l’andamento delle terapie o delle acquisizioni diagnostiche in generale.

---

## Sommario

- [Overview](#overview)
- [Requisiti](#requisiti)
- [Struttura del Progetto](#struttura-del-progetto)
- [Installazione](#installazione)
- [Configurazione](#configurazione)
- [Modalità di Esecuzione](#modalità-di-esecuzione)
  - [Modalità Terapia](#modalità-terapia)
  - [Modalità Diagnostica](#modalità-diagnostica)
- [Metriche Calcolate](#metriche-calcolate)
  - [Analisi Terapia](#analisi-terapia)
  - [Analisi Diagnostica](#analisi-diagnostica)
- [Output Generati](#output-generati)
- [Come Usare ed Estendere il Codice](#come-usare-ed-estendere-il-codice)
- [Licenza](#licenza)

## Overview

Il software esegue i seguenti step:

1. **Caricamento e Pulizia dei Dati**  
   - Vengono letti i file CSV (con attenzione ai separatori decimali, spazi extra e duplicati).  
   - I timestamp vengono convertiti in formato `datetime` e impostati come indice (ma mantenuti anche come colonna per facilitare il plotting).

2. **Sincronizzazione e Allineamento**  
   - I dati di injection e controlateral vengono sincronizzati (con eventuali correzioni di shift temporali).  
   - Vengono poi allineati su una griglia temporale regolare (con step di 1 secondo).

3. **Analisi del Picco**  
   - Calcolo del picco (tempo e valore).  
   - Calcolo della media dei dati filtrati.  
   - Identificazione del tempo al plateau (ad esempio, il tempo in cui la dose raggiunge il 90% del plateau).

4. **Calcolo di Metriche Aggiuntive**  
   - Per **terapia** (tempo al 90% per injection e controlateral, AUC-delta, slope iniziale, ratio a intervalli...).  
   - Per **diagnostica** (colonne normalizzate in minuscolo, calcolo di picchi e plateau su "dose_rate").

5. **Plot dei Risultati**  
   - Grafici annotati con curve di injection e controlateral.
   - Annotazioni per t₉₀, slope, ratio, ecc.

6. **Salvataggio dei Risultati in Excel**  
   - File `risultati_finali.xlsx`, con fogli "Stats", "Delta" e "Ratio".

---

## Requisiti

- **Python 3.7+**
- Librerie Python:
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `scipy`
  - `xlsxwriter` (oppure `openpyxl`)
  - `argparse`

Installa le dipendenze con:

```bash
pip install -r requirements.txt


---

### **BLOCCO 3** (struttura, installazione, configurazione)

```markdown
## Struttura del Progetto

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

---

### **BLOCCO 4** (modalità esecuzione e metriche calcolate)

```markdown
## Modalità di Esecuzione

Il software viene eseguito tramite il file `main.py`.

### Modalità Terapia

Per avviare l’analisi in modalità terapia:

```bash
python main.py --mode therapy


---

### **BLOCCO 5** (output, come usare ed estendere, licenza)

```markdown
## Output Generati

1. **Grafici Annotati**  
   - Curve di injection e controlateral.  
   - Annotazioni per tempi al 90%, slope, ratio, ecc.  
   - Salvati nella directory definita in `config.py` (ad es. `PATH_GRAFICI_THERAPY`).

2. **File Excel `risultati_finali.xlsx`**  
   - Creato nella stessa cartella dei grafici.  
   - Contiene tre fogli principali:
     - **Stats**: statistiche generali.  
     - **Delta**: delta calcolati a determinati time-point (se usati).  
     - **Ratio**: metriche relative ai rapporti (ratio a intervalli, media, max).

---

## Come Usare ed Estendere il Codice

1. **Configurazione:**
   - Modifica `config.py` per i percorsi (dati, grafici), i dizionari delle colonne e la modalità (`ANALYSIS_MODE`).

2. **Esecuzione:**
   - Lancia:
     ```bash
     python main.py --mode therapy
     ```
     oppure
     ```bash
     python main.py --mode diagnostic
     ```
   - I dati verranno caricati, analizzati e salvati in Excel.

3. **Output:**
   - Grafici annotati nella directory definita (es. `PATH_GRAFICI_THERAPY`), uno per ogni paziente.  
   - File Excel `risultati_finali.xlsx` con i fogli "Stats", "Delta" e "Ratio".

4. **Estensione:**
   - Il progetto utilizza una classe base astratta `BaseAnalysis` (in `analysis/base_analysis.py`) per definire il flusso di lavoro.  
   - Le classi `TherapyAnalysis` e `DiagnosticAnalysis` (in `analysis/therapy_analysis.py` e `analysis/diagnostic_analysis.py`) implementano la logica specifica per ciascuna modalità.  
   - Per aggiungere nuove metriche, puoi modificare o estendere le funzioni `analyze_peak`, `compute_therapy_metrics` (terapia) o quelle specifiche per la diagnostica.  
   - Per personalizzare i grafici, modifica la funzione di plotting in `plot_manager.py`, che accetta due dizionari (`stats` e `ratio_stats`) per annotare linee verticali, marker e testi sul grafico.

---

## Licenza

*(Inserisci qui il testo della licenza o il riferimento alla licenza applicata al tuo progetto.)*

