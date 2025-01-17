# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 11:51:30 2025

@author: nicop
"""

from datetime import timedelta
import numpy as np

def synchronize_data(df_inj, df_con):
    """
    Sincronizza i dati di iniezione e controlaterali.
    """
    delta = np.abs(df_inj.index[0] - df_con.index[0])
    minutes = delta.total_seconds() / 60
    if minutes > 50:
        if df_inj.index[0] > df_con.index[0]:
            df_inj.index -= timedelta(minutes=58.4)
        else:
            df_con.index -= timedelta(minutes=58.4)
    return df_inj, df_con
