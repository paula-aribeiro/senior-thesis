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


class Formula:
    def __init__(self, dep_var='A3',
                 terms=['C', 'I(C**2)', 'I(C*Mn)', 'I(C*Si)', 'I(C*Cr)', 'I(C*Ni)',
                        'Mn', 'I(Mn**2)', 'I(Mn*Si)', 'I(Mn*Cr)', 'I(Mn*Ni)',
                        'Si', 'I(Si*Si)', 'I(Si*Cr)', 'I(Si*Ni)',
                        'Cr', 'I(Cr**2)', 'I(Cr*Ni)',
                        'Ni', 'I(Ni**2)']):
        self.dep_var = dep_var
        self.terms = terms.copy()

    def dropterms(self, drop=[]):
        if isinstance(drop, str):
            drop = [drop]

        for term in drop:
            term = term.replace(' ', '')
            self.terms.remove(term)

    @property
    def formula(self):
        formula = '{} ~ '.format(self.dep_var)
        formula += ' + '.join(self.terms)

        return formula


def filter_terms_by_pvalue(results, maxpvalue=.05):
    pvalues = results.pvalues.sort_values(ascending=False)
    return list(pvalues.index[pvalues > maxpvalue])


if __name__ == '__main__':
    dataset = load_dataset('../databases/Tcritical.csv')

    # filter dataset
    criteria = dataset.eutectoid == 'hipo'
    filtered_dataset = dataset[criteria]

    # dependent variable
    dep_var = 'A1prime'

    # initialize formula
    poly_2nd_deg = Formula(dep_var)
    print(poly_2nd_deg.formula)

    # initialize regression; ols stands for 'ordinary least squares'
    reg = smf.ols(poly_2nd_deg.formula, data=filtered_dataset)
    # fit
    results = reg.fit()
    # print(results.summary())
    it = 1

    # maximum accepted p-value
    maxpvalue = .01
    # get terms with pvalue > maxpvalue
    dropterms = filter_terms_by_pvalue(results, maxpvalue)

    while len(dropterms) > 0:
        # drop terms with p-value > maxpvalue
        poly_2nd_deg.dropterms(dropterms[0])

        reg = smf.ols(poly_2nd_deg.formula, data=filtered_dataset)
        results = reg.fit()
        # print(results.summary())
        it += 1

        dropterms = filter_terms_by_pvalue(results, maxpvalue)

    print(results.summary())

    print(reg.formula)
    print('{} iteration(s)'.format(it))


    fig, ax = plt.subplots()

    exp = reg.endog
    pred = results.predict()
    ax.plot(exp, pred, 'kx')
    ax.plot([exp.min(), exp.max()], [exp.min(), exp.max()], 'r-')