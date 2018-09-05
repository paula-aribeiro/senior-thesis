# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model


# Creating dummy dataset
X, Y = np.mgrid[0:1.01:.01, 0:1.01:.01]  # X and Y grids
Z = .1 + .2*X + .3*Y + .4*X*Y + .5*X**2 + .6*Y**2  # Z = f(X, Y)
# random_sample interval: [0, 1] --> noise interval: [-1, 1]
noise = (2*np.random.random_sample(Z.shape) - 1)
Z += noise/10  # add noise to Z

# Visualizing f(X, Y)
fig1, ax1 = plt.subplots()
dummy_map = ax1.pcolormesh(X, Y, Z)
fig1.colorbar(dummy_map, ax=ax1)

# X, Y 2D arrays --> 1D array
x, y, z = X.ravel(), Y.ravel(), Z.ravel()

# Preparing data to poly.fit_transform
# Merge x, y 1D arrays in a single numpy array
# ind_var is the independent variables
ind_var = np.vstack([x, y]).T
# dep_var is the dependent variable
dep_var = z

# https://stackoverflow.com/questions/20463226/how-to-do-gaussian-polynomial-regression-with-scikit-learn
# http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html
poly = PolynomialFeatures(degree=2)
# x, y --> 1, x, y, x*y, x^2, y^2
ind_var_ = poly.fit_transform(ind_var)

# Linear regression
clf = linear_model.LinearRegression()
clf.fit(ind_var_, dep_var)  # data fitted, yay!

# Predict fitted values
predict = [[0, 0], [.5, .5]]
predict_ = poly.fit_transform(predict)
print(clf.predict(predict_))

fig2, ax2 = plt.subplots()
# Plotting fitted data for iso-values of Y
for j in range(Y.shape[-1])[::20]:
    predict = np.vstack([X[:, j], Y[:, j]]).T
    predict_ = poly.fit_transform(predict)

    ax2.plot(X[:, j], Z[:, j], label='Y = {:g}'.format(Y[0, j]))
    ax2.plot(X[:, j], clf.predict(predict_), 'k--')

ax2.legend()

plt.show()
