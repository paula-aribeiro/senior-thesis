# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
from pandas.plotting import scatter_matrix

import statsmodels.api as sm
import statsmodels.formula.api as smf

from statsmodels.sandbox.regression.predstd import wls_prediction_std


def load_dataset(fname):
    # read dataset
    dataset = pd.read_csv(fname, comment='#')

    # compositions to wt.%
    dataset.C *= 100
    dataset.Mn *= 100
    dataset.Si *= 100
    dataset.Cr *= 100
    dataset.Ni *= 100

    # temperatures to oC
    dataset.A1 -= 273.15
    dataset.A1prime -= 273.15
    dataset.A3 -= 273.15

    return dataset


if __name__ == '__main__':
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
    dataset = load_dataset(fname_dataset)

    # Hipoeutectoid
    filtered_dataset = dataset[dataset.eutectoid == 'hipo']

    # regression
    formula = ('A3 ~ C + I(C**2) + I(C*Mn) + I(C*Si) + I(C*Cr) + I(C*Ni)  + '
               'Mn + I(Mn**2) + I(Mn*Si) + I(Mn*Cr) + I(Mn*Ni)  + '
               'Si + I(Si*Si) + I(Si*Cr) + I(Si*Ni)  + '
               'Cr + I(Cr**2) + I(Cr*Ni) + '
               'Ni + I(Ni**2)')

    reg = smf.ols(formula, data=filtered_dataset)

    results = reg.fit()

    print(results.summary())
