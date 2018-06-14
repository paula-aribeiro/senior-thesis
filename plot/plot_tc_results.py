import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tctools import load_table, plot_table

files = pd.read_csv('../databases/compositions_files.csv')

fig, ax = plt.subplots()

for i, fname in enumerate(files['file']):
    if i%10 == 0:
        try:
            df = load_table(fname, 'T', fill=0)
            x = df['T']
            if 'NP(FCC_A1#1)' in df.columns:
                y = df['NP(FCC_A1#1)']
            if 'NP(FCC_A1#2)' in df.columns:
                y = df['NP(FCC_A1#2)']
            ax.plot(x, y, label=fname)
        except Exception as ex:
            print(fname, ex)

# plt.legend()
plt.show()
