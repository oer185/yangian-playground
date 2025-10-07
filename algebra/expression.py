class Expression:
    def __init__(self, terms):
        self.terms = terms

    def __add__(self, other):
        if isinstance(other, Expression):
            return Sum([self, other])
        return Sum([self, Expression([other])])

    def __mul__(self, other):
        if isinstance(other, Expression):
            return Expression(self.terms + other.terms)
        return Expression(self.terms + [other])

    def prepend(self, x):
        return Expression([x] + self.terms)

    def __repr__(self):
        return " * ".join(str(t) for t in self.terms)


class Sum:
    def __init__(self, exprs):
        self.exprs = exprs

    def __add__(self, other):
        if isinstance(other, Sum):
            return Sum(self.exprs + other.exprs)
        return Sum(self.exprs + [other])

    def __repr__(self):
        return " + ".join(str(e) for e in self.exprs)


class ScalarMultiple:
    def __init__(self, scalar, expr):
        self.scalar = scalar
        self.expr = expr

    def __repr__(self):
        return f"{self.scalar} * ({self.expr})"
