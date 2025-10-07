import sympy as sp


class T(sp.Function):
    nargs = 3

    @classmethod
    def eval(cls, i, j, r):
        return None

    def _sympystr(self, printer):
        i, j, r = self.args
        return f"T_{{{i}{j}}}^({r})"

    def _latex(self, printer=None):
        i, j, r = self.args
        return f"T_{{{i}{j}}}^{{({r})}}"

    def __str__(self):
        return self._sympystr(None)

    def __repr__(self):
        return self._sympystr(None)
