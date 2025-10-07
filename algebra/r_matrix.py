import sympy as sp


def identity_matrix(n):
    return sp.eye(n * n)


def permutation_matrix(n):
    P = sp.zeros(n * n, n * n)
    for i in range(n):
        for j in range(n):
            row = i * n + j
            col = j * n + i
            P[row, col] = 1
    return P


def R_matrix(z, n=2):
    """Return R(z) = I + P/z for GL(n)"""
    I = identity_matrix(n)
    P = permutation_matrix(n)
    return I + P / z

