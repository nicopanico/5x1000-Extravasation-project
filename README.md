# 📊 Analisi Dati per Terapia e Diagnostica

Questo repository contiene un insieme di script Python per l'analisi dei dati relativi a **terapie** e **acquisizioni diagnostiche**.  
Il progetto è stato sviluppato per confrontare i dati di **injection** e **controlateral** provenienti da dosimetri (o sistemi analoghi) e per calcolare statistiche e metriche aggiuntive utili a:

- **Identificare casi di stravaso** (quando l’andamento della dose nel braccio di injection risulta anomalo).
- **Caratterizzare e confrontare l’andamento delle terapie o delle acquisizioni diagnostiche** in generale.

---

## 📌 Sommario

- [Overview](#-overview)
- [Requisiti](#-requisiti)
- [Struttura del Progetto](#-struttura-del-progetto)
- [Installazione](#-installazione)
- [Configurazione](#-configurazione)
- [Modalità di Esecuzione](#-modalità-di-esecuzione)
  - [Modalità Terapia](#-modalità-terapia)
  - [Modalità Diagnostica](#-modalità-diagnostica)
- [Metriche Calcolate](#-metriche-calcolate)
  - [Analisi Terapia](#-analisi-terapia)
  - [Analisi Diagnostica](#-analisi-diagnostica)
- [Output Generati](#-output-generati)
- [Come Usare ed Estendere il Codice](#-come-usare-ed-estendere-il-codice)
- [Licenza](#-licenza)

---

## 🔍 Overview

Il software esegue i seguenti passaggi:

1. **Caricamento e Pulizia dei Dati**  
   - Lettura dei file CSV con gestione dei separatori decimali, spazi extra e duplicati.
   - Conversione dei timestamp in formato `datetime`, con impostazione come indice.

2. **Sincronizzazione e Allineamento**  
   - Sincronizzazione dei dati di injection e controlateral (correzione di eventuali shift temporali).
   - Allineamento su una griglia temporale regolare (step di 1 secondo).

3. **Analisi del Picco**  
   - Identificazione del **tempo e valore di picco**.
   - Calcolo della **media dei dati filtrati**.
   - Determinazione del **tempo al plateau** (tempo in cui la dose raggiunge il 90% del plateau).

4. **Calcolo di Metriche Aggiuntive**  
   - **Terapia:** tempo al 90% per injection e controlateral, AUC-delta, slope iniziale, ratio a intervalli.
   - **Diagnostica:** normalizzazione delle colonne, calcolo di picchi e plateau su *dose_rate*.

5. **Plot dei Risultati**  
   - Grafici annotati con curve di injection e controlateral.
   - Annotazioni per t₉₀, slope, ratio, ecc.

6. **Salvataggio dei Risultati in Excel**  
   - File `risultati_finali.xlsx`, con i fogli: `"Stats"`, `"Delta"` e `"Ratio"`.

---

## 🔧 Requisiti

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


