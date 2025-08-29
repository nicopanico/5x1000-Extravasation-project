# -*- coding: utf-8 -*-

"""
Created on Fri Jan 17 11:54:38 2025

@author: nicop
"""

# main.py
import argparse
from analysis.inj_only_analysis import InjectionOnlyAnalysis
from config import ANALYSIS_MODE, ROOT_INJECTIONS_THERAPY, ROOT_CONTROLATERALS_THERAPY, \
                   ROOT_INJECTIONS_DIAGNOSTIC, ROOT_CONTROLATERALS_DIAGNOSTIC, \
                   PATH_GRAFICI_THERAPY, PATH_GRAFICI_DIAGNOSTIC
from data_manager import DataManager
from analysis.therapy_analysis import TherapyAnalysis
from analysis.diagnostic_analysis import DiagnosticAnalysis

def main():
    parser = argparse.ArgumentParser(description="Analisi dei dati: Terapia o Diagnostica")
    parser.add_argument(
        "--mode",
        choices=["therapy", "diagnostic", "inj_only"],  # <— aggiungi
        default=ANALYSIS_MODE,
        help="Modalità di analisi: 'therapy', 'diagnostic' o 'inj_only'"
    )
    args = parser.parse_args()

    # Seleziona i path e i parametri in base alla modalità
    if args.mode == "therapy":
        root_injection = ROOT_INJECTIONS_THERAPY
        root_controlateral = ROOT_CONTROLATERALS_THERAPY
        output_dir = PATH_GRAFICI_THERAPY
        analysis_class = TherapyAnalysis
    elif args.mode == "diagnostic":
        root_injection = ROOT_INJECTIONS_DIAGNOSTIC
        root_controlateral = ROOT_CONTROLATERALS_DIAGNOSTIC
        output_dir = PATH_GRAFICI_DIAGNOSTIC
        analysis_class = DiagnosticAnalysis
    else:
        root_injection = ROOT_INJECTIONS_DIAGNOSTIC
        root_controlateral = ROOT_CONTROLATERALS_DIAGNOSTIC  # non usato
        output_dir = PATH_GRAFICI_DIAGNOSTIC
        analysis_class = InjectionOnlyAnalysis

    # Istanzia il DataManager con i path appropriati
    data_manager = DataManager(root_injection=root_injection, root_controlateral=root_controlateral)
    
    # Istanzia l'analisi
    analysis = analysis_class(data_manager, output_dir)
    
    # Esegui l'analisi
    analysis.run_analysis()

if __name__ == "__main__":
    main()


