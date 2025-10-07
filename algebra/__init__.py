from algebra.generator import Generator

T = lambda i, j, r: Generator(i, j, r)

a = T(1, 2, 1)
b = T(2, 1, 2)

expr = a * b + 2 * a
print(expr)
