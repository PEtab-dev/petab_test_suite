import numpy as np


def x(p, x0, ts):
    """
    States via analytic solution of ODE.
    Returns an array of shape n_x * n_t.
    """
    p0 = p.get('p0', 0.06)
    p1 = p.get('p1', 0.08)
    n_t = len(ts)
    sol = np.zeros((2, n_t))
    for ix, t in enumerate(ts):
        e = np.exp(- (p0 + p1) * t)
        A = 1 / (- p0 - p1) * np.array([[- p1 - p0 * e, - p1 + p1 * e],
                                        [- p0 + p0 * e, - p0 - p1 * e]])
        sol[:, ix] = np.dot(A, x0).flatten()
    return sol


