import Tcritical_regression_statsmodels as tr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import root
from parse_database import read_header_database, parse_header_database
from plot_carbon_isopleth import (load_reshape_dataset,
                                  select_carbon_isopleth,
                                  plot_carbon_isopleth)

fname_dataset = '../databases/Tcritical.csv'

header = read_header_database(fname_dataset)
# Temperature range and compositions ranges
Trange, crange = parse_header_database(header)

# dataset as pandas DataFrame
dataset = tr.load_dataset(fname_dataset)

# dependent variable
dep_var = 'A1'

reg, results = {}, {}

reg, results = tr.regression_poly_2nd_deg(
    dataset=dataset,
    dep_var=dep_var, maxpvalue=.01,
    printsummary=False)

ax = tr.plot_fitting_results(results, dataset, dep_var)
ax.set_title('{}'.format(dep_var))

print(results.summary())


def A1(C=0, Mn=0, Si=0, Cr=0, Ni=0):
    """
    A1 temperature for either alloy
    """
    def T(C):
        df = pd.DataFrame(dict(C=C, Mn=Mn, Si=Si, Cr=Cr, Ni=Ni))
        return results.predict(df)

    T = np.ndarray(C.shape)

    return T

# plot isopleths
fig, ax = plt.subplots()

# multidimensional dataset as ordered dictionary
dataset_multi = load_reshape_dataset(fname_dataset)

# compositions (level)
Mn = 0
Si = 0
Cr = 0
Ni = 0

# compositions (wt.%)
C_ = 100*np.linspace(crange['C'].min, crange['C'].max, 100)

for Mn in range(5):
    # compositions (wt.%)
    Mn_ = 100*crange['Mn'].array[Mn]
    Si_ = 100*crange['Si'].array[Si]
    Cr_ = 100*crange['Cr'].array[Cr]
    Ni_ = 100*crange['Ni'].array[Ni]

    # experimental isopleth
    isopleth = select_carbon_isopleth(dataset_multi, Mn, Si, Cr, Ni)

    line, = plot_carbon_isopleth(isopleth, dep_var, ax,
                                 ls='none', marker='x',
                                 annotate=True)

    # predicted isopleth
    ax.plot(C_, A1(C_, Mn_, Si_, Cr_, Ni_), color=line.get_color())

plt.show()
