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
  - [Modalità Terapia](#modalità-terapia)
  - [Modalità Diagnostica](#modalità-diagnostica)
- [Metriche Calcolate](#-metriche-calcolate)
  - [Analisi Terapia](#analisi-terapia)
  - [Analisi Diagnostica](#analisi-diagnostica)
- [Output Generati](#-output-generati)
- [Come Usare ed Estendere il Codice](#-come-usare-ed-estendere-il-codice)
- [Licenza](#-licenza)

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



