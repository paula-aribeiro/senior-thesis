"""
Extract critical temperatures from Thermo-Calc generated tables for randim
compositions
"""

if __name__ == '__main__':
    import numpy as np
    import pandas as pd
    from progressbar import ProgressBar

    # local modules
    from extract_Tcrit import extract_Tcrit

    # compositions database
    fname = '../databases/random_compositions_database.csv'
    db = pd.read_csv(fname)

    n = len(db)  # number of rows
    file = np.full(n, None)
    A1 = np.full(n, np.nan)
    A1prime = np.full(n, np.nan)
    A3 = np.full(n, np.nan)
    eutectoid = np.full(n, None)

    pbar = ProgressBar(maxval=n).start()
    for idx in range(n):
        fname = '../results/RANDOM_COMPOSITIONS_DATABASE_{:05d}.DAT'.format(idx)
        file[idx] = fname
        A1[idx], A1prime[idx], A3[idx], eutectoid[idx] = extract_Tcrit(fname)
        pbar.update(idx)

    db['file'] = file
    db['A1'] = A1
    db['A1prime'] = A1prime
    db['A3'] = A3
    db['eutectoid'] = eutectoid
    db = db[['file','C','Mn','Si','Cr','Ni','A1','A1prime','A3','eutectoid']]

    fname = '../databases/Tcritical_random_compositions_database.csv'
    file = open(fname, 'w')
    file.close()
    db.to_csv(fname, index=False, mode='a')
