import sympy as sp
from .r_matrix import R_matrix
from .t_matrix import T_matrix


def check_RTT_relation(z, w):
    R = R_matrix(z - w)
    Tz = T_matrix(z)
    Tw = T_matrix(w)

    T1 = sp.kronecker_product(Tz, sp.eye(2))
    T2 = sp.kronecker_product(sp.eye(2), Tw)

    lhs = sp.simplify(R * T1 * T2)
    rhs = sp.simplify(T2 * T1 * R)

    diff = sp.simplify(lhs - rhs)
    print("Difference:")
    sp.pprint(diff)

    return diff == sp.zeros(4, 4)


def extract_commutators_from_rtt(z, w):
    R = R_matrix(z - w)
    Tz = T_matrix(z)
    Tw = T_matrix(w)

    T1 = sp.kronecker_product(Tz, sp.eye(2))
    T2 = sp.kronecker_product(sp.eye(2), Tw)

    lhs = sp.expand(R * T1 * T2)
    rhs = sp.expand(T2 * T1 * R)

    diff = lhs - rhs
    print("📤 Commutation relations from RTT:\n")

    for i in range(diff.shape[0]):
        for j in range(diff.shape[1]):
            expr = sp.simplify(diff[i, j])
            if expr != 0:
                print(f"({i},{j}):")
                sp.pprint(expr)
                print("-" * 60)
