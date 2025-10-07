class Generator:
    def __init__(self, i, j, r):
        self.i = i
        self.j = j
        self.r = r

    def __repr__(self):
        return f"T_{{{self.i}{self.j}}}^({self.r})"

    def __mul__(self, other):
        from .expression import Expression
        return Expression([self]) * other

    def __rmul__(self, scalar):
        from .expression import Expression
        return Expression([self]) * scalar
