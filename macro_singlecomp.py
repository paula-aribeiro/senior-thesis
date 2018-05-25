import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tctools import load_table, plot_table

if __name__ == '__main__':
    if len(sys.argv) > 1:
        T_min, T_max, T_step = 673, 1473, 10
        df = pd.read_csv('files_list.csv')

        for idx in sys.argv[1:]:
            fname = 'results/{:05d}.DAT'.format(int(idx))
            
            fig, ax = plt.subplots()
            result = load_table(fname, sort='T', fill=0)
            plot_table(df=result, xaxis='T', ax=ax, colpattern='NP(*)')
            plt.pause(.05)
            fig.show()
            
            idx, = np.where(fname == df['file'].values)
            if len(idx) > 0:
                idx = int(idx[0])
            else:
                continue

            row = df.iloc[[idx]]

            # Generates macro
            fmacro = open('macro_singlecomp.tcm', 'w')
            fmacro.write(('go data\n'
                          'def-el fe c mn si cr ni\n'
                          'rej ph *\n'
                          'rest ph fcc bcc cem\n'
                          'get\n'
                          'go p-3\n\n'
                          'ent-sy tab blab\n'
                          't x(*,*) np(*);\n\n'
                          's-a-v 1 t {:d} {:d} {:d}\n\n').format(T_min, T_max, T_step))

            wC = float(row['C'].values)
            wMn = float(row['Mn'].values)
            wSi = float(row['Si'].values)
            wCr = float(row['Cr'].values)
            wNi = float(row['Ni'].values)

            fmacro.write(('s-c n=1 p=101325 t=1173\n'
                          's-c w(c)={:e} w(mn)={:e} w(si)={:e}\n'
                          's-c w(cr)={:e} w(ni)={:e}\n'
                          'c-e\n'
                          'c-e\n').format(wC, wMn, wSi, wCr, wNi))

            fmacro.write(('step,,\n'
                          'post\n'
                          's-l f\n'
                          's-d-a x t-c\n'
                          'plot,,\n'))

            fmacro.write('set-int')
            fmacro.close()

            os.system('thermocalc macro_singlecomp.tcm')
            
            print(row)
