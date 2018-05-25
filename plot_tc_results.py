import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tctools import load_table, plot_table

files = pd.read_csv('files_list.csv')

fig, ax = plt.subplots()

for i, fname in enumerate(files['file']):
    if i%100 == 0:
        try:
            df = load_table(fname, 'T', fill=0)
            plot_table(df, 'T', ax=ax, colpattern='NP(*)', legend=False)
        except:
            print(fname)

plt.show()
