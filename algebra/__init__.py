from algebra.generator import T

Tmap = lambda i, j, r: T(i, j, r)

a = Tmap(1, 2, 1)
b = Tmap(2, 1, 2)

expr = a * b + 2 * a
print(expr)
