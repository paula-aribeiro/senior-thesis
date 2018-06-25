"""
Extract critical temperatures (A1, A1', and A3) from Thermo-Calc 
generated tables
"""

import glob
import sys
import numpy as np
import pandas as pd
from tctools import load_table, plot_table
# local module
from parse_database import read_header_database


def extract_Tcrit(fname):
    A1, A1prime, A3, eutectoid = np.nan, np.nan, np.nan, None

    try:
        df = load_table(fname, sort='T', fill=0)
    except:
        print('Failed to load {}'.format(fname))
    else:
        # temperature
        T = df['T']
        mf_fer = np.array([])
        mf_aus = np.array([])
        mf_cem = np.array([])

        if 'NP(BCC_A2)' in df.columns:
            # mole fraction of ferrite
            mf_fer = df['NP(BCC_A2)']

        max_aus = 0  # 0 K
        if 'NP(FCC_A1#1)' in df.columns:
            # mole fraction of austenite
            mf_aus = df['NP(FCC_A1#1)']
            max_aus = mf_aus.max()
        if 'NP(FCC_A1#2)' in df.columns:
            # Chooses the column with higher NP values
            if df['NP(FCC_A1#2)'].max() > max_aus:
                mf_aus = df['NP(FCC_A1#2)']

        if 'NP(CEMENTITE)' in df.columns:
            # mole fraction of cementite
            mf_cem = df['NP(CEMENTITE)']

        # Determine A1 and A3
        if len(mf_aus) > 0:
            # A1 temperature
            # highest temperature where mf_aus is 0
            idx, = np.where(mf_aus == 0)
            if len(idx) > 0:
                A1 = T[idx[-1]]

            # A3 temperature
            # lowest temperature where mf_aus is 1
            idx, = np.where(mf_aus == 1)
            if len(idx) > 0:
                A3 = T[idx[0]]

            # Determine A1'
            idx_fer, = np.where(mf_fer == 0)
            idx_cem, = np.where(mf_cem == 0)

            if len(idx_fer) > 0:
                if len(idx_cem) > 0:
                    # A1' and A3 are related to the temperatures where
                    # mf_fer and mf_cem are 0, namely T_fer and T_cem
                    # A1' equals to min(T_fer, T_cem)
                    # A3 equals to max(T_fer, T_cem)
                    T_fer = T[idx_fer[0]]
                    T_cem = T[idx_cem[0]]

                    if T_fer > T_cem:
                        A1prime = T_cem
                        A3 = T_fer
                        eutectoid = 'hipo'
                    else:
                        A1prime = T_fer
                        A3 = T_cem
                        eutectoid = 'hiper'
                else:
                    # If cementite is not defined, there's no intecritical
                    # phases field (ferrite + austenite + cementite).
                    # In this case, we assume A1 = A1' and A3 is the lowest
                    # temperature where mf_fer is 0
                    A1prime = A1
                    eutectoid = 'hipo'
            else:
                if len(mf_cem) > 0:
                    eutectoid = 'hiper'
        else:
            print('{} has no austenite'.format(fname))

    return A1, A1prime, A3, eutectoid


if __name__ == '__main__':
    # database
    fname = '../databases/compositions_files.csv'
    header = read_header_database(fname)
    db = pd.read_csv(fname, comment='#')

    n = len(db)
    A1 = np.full(n, np.nan)
    A1prime = np.full(n, np.nan)
    A3 = np.full(n, np.nan)
    eutectoid = np.full(n, None)

    for i, fname in enumerate(db['file']):
        A1[i], A1prime[i], A3[i], eutectoid[i] = extract_Tcrit(fname)

    db['A1'] = A1
    db['A1prime'] = A1prime
    db['A3'] = A3
    db['eutectoid'] = eutectoid

    fname = '../databases/Tcritical.csv'
    file = open(fname, 'w')
    file.write(header)
    file.close()
    db.to_csv(fname, index=False, mode='a')
