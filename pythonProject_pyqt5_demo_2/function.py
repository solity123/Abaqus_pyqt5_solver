import numpy as np

def objective(x):
    return sum(xi ** 2 for xi in x)

def constraint(x):
    return np.all(x >= 0) and np.sum(x) <= 5
