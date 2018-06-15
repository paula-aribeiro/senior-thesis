import glob
import sys
import numpy as np
import pandas as pd
from tctools import load_table, plot_table

database = pd.read_csv('../databases/compositions_files.csv')

n = len(database)
A1 = np.full(n, np.nan)
A1prime = np.full(n, np.nan)
A3 = np.full(n, np.nan)

for i, fname in enumerate(database['file']):
    try:
        df = load_table(fname, sort='T', fill=0)
    except:
        print(fname, 'failed!')
    else:
        # temperature
        T = df['T']

        mf_fer, idx_fer = [], []
        if 'NP(BCC_A2)' in df.columns:
            # mole fraction of ferrite
            mf_fer = df['NP(BCC_A2)']
            idx_fer, = np.where(mf_fer.values == 0)
        else:
            print('No bcc phase in {}'.format(fname))

        mf_aus, idx_aus = [], []
        if 'NP(FCC_A1#1)' in df.columns:
            # mole fraction of austenite
            # FCC_A1#1 is the default interpretation
            mf_aus = df['NP(FCC_A1#1)']
            idx_aus, = np.where(mf_aus.values == 0)
        elif 'NP(FCC_A1#2)' in df.columns:
            mf_aus = df['NP(FCC_A1#2)']
            idx_aus, = np.where(mf_aus.values == 0)
        else:
            print('No fcc phase in {}'.format(fname))

        mf_cem, idx_cem = [], []
        if 'NP(CEMENTITE)' in df.columns:
            # mole fraction of cementite
            mf_cem = df['NP(CEMENTITE)']
            idx_cem, = np.where(mf_cem.values == 0)

        # if idx_fer and idx_aus are greater than zero
        if len(idx_fer) > 0 and len(idx_aus) > 0:

            # A1 temperature
            # lowest temperature where mf_aus is 0
            A1[i] = T[idx_aus[-1]]

            # A1' and A3 temperatures
            if len(idx_cem) > 0:
                # A1' and A3 are related to the temperatures where
                # mf_fer and mf_cem are 0, namely T_fer and T_cem
                # A1' equals to min(T_fer, T_cem)
                # A3 equals to max(T_fer, T_cem)
                T_fer = T[idx_fer[0]]
                T_cem = T[idx_cem[0]]

                if T_fer < T_cem:
                    A1prime[i] = T_fer
                    A3[i] = T_cem
                else:
                    A1prime[i] = T_cem
                    A3[i] = T_fer
            else:
                # If cementite is not defined, there's no intecritical
                # phases field (ferrite + austenite + cementite).
                # In this case, we assume A1 = A1' and A3 is the lowest
                # temperature where mf_fer is 0
                A1prime[i] = A1[i]
                A3[i] = T[idx_fer[0]]

        if i == 200:
            break

database['A1'] = A1
database['A1prime'] = A1prime
database['A3'] = A3

database.to_csv('../databases/Tcritical.csv', index=False)
