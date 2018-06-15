"""
Given a simulation with index #, plot corresponding 
RESULT_####.TXT and compare to Thermo-Calc macro simulation
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tctools import load_table, plot_table

if __name__ == '__main__':
    if len(sys.argv) > 1:
        T_min, T_max, T_step = 673, 1473, 10
        df = pd.read_csv('../databases/compositions_files.csv')

        for idx in sys.argv[1:]:
            fname = '../results/{:05d}.DAT'.format(int(idx))

            fig, ax = plt.subplots()
            result = load_table(fname, sort='T', fill=0)
            plot_table(df=result, xaxis='T', ax=ax, colpattern='NP(*)')

            idx, = np.where(fname == df['file'].values)
            if len(idx) > 0:
                idx = int(idx[0])
            
            sel = df.iloc[idx]
            title = 'Fe-{:g}C-{:g}Mn-{:g}Si-{:g}Ni-{:g}Cr'.format(
                100*sel['C'], 100*sel['Mn'], 100*sel['Si'], 100*sel['Ni'], 100*sel['Cr'])
            ax.set_title(title)

            plt.show()
