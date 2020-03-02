import numpy as np

a0 = 1
b0 = 0
k1 = 0.8
k2 = 0.6

ts = [0, 10]


def analytical_a(t, a0=a0, b0=b0, k1=k1, k2=k2):
    return k2 * (a0 + b0) / (k1 + k2) \
           + (a0 - k2 * (a0 + b0) / (k1 + k2)) * np.exp(-(k1 + k2) * t)


def analytical_b(t, a0=a0, b0=b0, k1=k1, k2=k2):
    return k1 * (a0 + b0) / (k1 + k2) \
           + (b0 - k1 * (a0 + b0) / (k1 + k2)) * np.exp(-(k1 + k2) * t)
