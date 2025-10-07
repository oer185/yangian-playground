from .generator import T
import sympy as sp


def T_matrix(z, max_order=2):
    Tmat = sp.Matrix(2, 2, lambda i, j: 0)
    for i in range(2):
        for j in range(2):
            entry = 0
            for r in range(1, max_order + 1):
                Tijr = T(i+1, j+1, r)
                entry += Tijr / z**r
            Tmat[i, j] = entry
    return Tmat
