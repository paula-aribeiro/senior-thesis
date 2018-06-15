import glob
import sys
import numpy as np
import pandas as pd
from tctools import load_table, plot_table

files = pd.read_csv('../databases/compositions_files.csv')

flist = []
hasbcc = []
hasfcc = []
hascem = []
Tinf = []
Tsup = []

for i, fname in enumerate(files['file']):
    try:
        df = load_table(fname, sort='T', fill=0)
    except:
        print(fname, 'failed!')
    else:
        flist.append(fname)
        
        hasbcc.append('NP(BCC_A2)' in df.columns)
        hasfcc.append('NP(FCC_A1#1)' in df.columns or 'NP(FCC_A1#2)' in df.columns)
        hascem.append('NP(CEMENTITE)' in df.columns)
        
        Tinf.append(np.min(df['T']))
        Tsup.append(np.max(df['T']))

df = pd.DataFrame(dict(file=flist, BCC_A2=hasbcc, FCC_A1=hasfcc,
                       CEMENTITE=hascem, Tinf=Tinf, Tsup=Tsup),
                  columns=['file', 'BCC_A2', 'FCC_A1', 'CEMENTITE',
                           'Tinf', 'Tsup'])


df.to_csv('../databases/check_np_temp_range.csv', index=False)
