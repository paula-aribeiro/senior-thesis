import glob
import sys
import numpy as np
import pandas as pd
from tctools import load_table, plot_table

files = pd.read_csv('files_list.csv')

flist = []
hasbcc = []
hasfcc = []
hascem = []


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

df = pd.DataFrame(dict(file=flist, hasbcc=hasbcc, hasfcc=hasfcc, hascem=hascem),
		columns=['file', 'hasbcc', 'hasfcc', 'hascem'])

df.to_csv('has_np.csv', index=False)
