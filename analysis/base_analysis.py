# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 16:02:03 2025

@author: PANICON
"""

# analysis/base_analysis.py
from abc import ABC, abstractmethod

class BaseAnalysis(ABC):
    def __init__(self, data_manager, output_dir):
        self.data_manager = data_manager
        self.output_dir = output_dir

    @abstractmethod
    def load_data(self):
        """Carica e pulisce i dati dai file (iniezioni e controlaterali)."""
        pass

    @abstractmethod
    def synchronize_and_align(self, df_inj, df_con, base_name):
        """Sincronizza e allinea i dati (eventualmente con regole specifiche)."""
        pass

    @abstractmethod
    def analyze_peak(self, df_inj, df_con):
        """Esegue l’analisi del picco e calcola le statistiche richieste."""
        pass

    @abstractmethod
    def plot_results(self, base_name, df_inj, df_con, df_inj_filtered, df_con_filtered):
        """Crea e salva i grafici dell’analisi."""
        pass

    def run_analysis(self):
        """
        Esegue l’analisi per tutti i file in comune.
        Il flusso tipico è:
          1. Ottenere i nomi base comuni
          2. Per ciascun nome:
             - Caricare i dati
             - Sincronizzare e allineare
             - Analizzare il picco e calcolare le statistiche
             - Eseguire eventuale analisi delta
             - Plot dei risultati
          3. Salvare i risultati complessivi (Excel, tabelle, ecc.)
        """
        # Esempio: ottieni i nomi base comuni (questo metodo potrebbe appartenere al DataManager)
        names = self.data_manager.get_file_names()
        all_stats = []  # lista di dizionari con statistiche
        skipped = []  # Lista per tenere traccia dei file/pazienti saltati
        # ciclo sui file
        for base_name in names:
            print(f"Processo: {base_name}")
            inj_path, con_path = self.data_manager.get_paths_for_base(base_name)
            # Carica e pulisci i dati
            df_inj = self.data_manager.load_and_clean_data(inj_path, self.get_injection_columns())
            df_con = self.data_manager.load_and_clean_data(con_path, self.get_controlateral_columns())
            if df_inj.empty or df_con.empty:
                print(f"Attenzione: {base_name} - uno dei DataFrame è vuoto. Skip.")
                skipped.append(base_name)
                continue
            # Sincronizza e allinea
            df_inj_sync, df_con_sync = self.synchronize_and_align(df_inj, df_con, base_name)
            
            if df_inj_sync.empty or df_con_sync.empty:
                print(f"Attenzione: {base_name} - la sincronizzazione ha restituito DataFrame vuoti. Skip.")
                skipped.append(base_name)
                continue
            # Analizza il picco (ed eventualmente filtra)
            df_inj_filtered, df_con_filtered, stats = self.analyze_peak(df_inj_sync, df_con_sync)
            stats["base_name"] = base_name
            all_stats.append(stats)
            # Plot dei risultati
            self.plot_results(base_name, df_inj_sync, df_con_sync, df_inj_filtered, df_con_filtered)
       
        if skipped:
            print("I seguenti pazienti sono stati saltati:")
            for name in skipped:
                print(name)
       
        

        