# scripts/metrics_utils.py
import numpy as np

def jain_index(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0 or np.all(x == 0): 
        return 0.0
    return float((x.sum()**2) / (n * (x**2).sum()))

def gini_coefficient(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0: 
        return 0.0
    # Ensure non-negative
    mn = x.min()
    if mn < 0: 
        x = x - mn
    s = x.sum()
    if s == 0: 
        return 0.0
    xs = np.sort(x)
    i = np.arange(1, n+1)
    # G = (2*sum(i*x_i))/(n*sum(x)) - (n+1)/n
    G = (2.0 * (i * xs).sum()) / (n * s) - (n + 1.0) / n
    return float(G)

def p5_percentile(x):
    x = np.asarray(x, dtype=float)
    if len(x) == 0: 
        return 0.0
    return float(np.percentile(x, 5))
