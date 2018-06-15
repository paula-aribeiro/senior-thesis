import glob
import sys
import numpy as np
import pandas as pd
from tctools import load_table, plot_table

comp_files = pd.read_csv('../databases/compositions_files.csv')

n = len(comp_files)
A1 = np.full(n, np.nan)
A1prime = np.full(n, np.nan)
A3 = np.full(n, np.nan)

for i, fname in enumerate(comp_files['file']):
    try:
        df = load_table(fname, sort='T', fill=0)
    except:
        print(fname, 'failed!')
    else:
        T = df['T']

        mf_fer, idx_fer = None, None
        if 'NP(BCC_A2)' in df.columns:
            # mole fraction of ferrite
            mf_fer = df['NP(BCC_A2)']
        else:
            print('No bcc phase in {}'.format(fname))

        mf_aus, idx_aus = None, None
        if 'NP(FCC_A1#1)' in df.columns:
            # mole fraction of austenite
            mf_aus = df['NP(FCC_A1#1)']
        elif 'NP(FCC_A1#2)' in df.columns:
            mf_aus = df['NP(FCC_A1#2)']
        else:
            print('No fcc phase in {}'.format(fname))

        mf_cem, idx_cem = None, None
        if 'NP(CEMENTITE)' in df.columns:
            mf_cem = df['NP(CEMENTITE)']
            idx_cem, = np.where(mf_cem.values == 0)

        if isinstance(idx_fer, np.ndarray) and isinstance(idx_aus, np.ndarray):
            idx_aus, = np.where(mf_aus.values == 0)
            idx_fer, = np.where(mf_fer.values == 0)

            # A1 temperature
            A1[i] = T[idx_aus[-1]]

            # A1' and A3 temperatures
            if idx_cem is None:
                A1prime[i] = A1[i]
                A3[i] = T[idx_fer[0]]
            else:
                if idx_cem[0] < idx_fer[0]:
                    A1prime[i] = T[idx_cem[0]]
                    A3[i] = T[idx_fer[0]]
                else:
                    A1prime[i] = T[idx_fer[0]]
                    A3[i] = T[idx_cem[0]]

#