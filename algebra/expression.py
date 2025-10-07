class Expression:
    def __init__(self, terms):
        self.terms = terms

    def __add__(self, other):
        return Expression(self.terms + other.terms)

    def __mul__(self, other):
        if isinstance(other, Expression):
            return Expression(self.terms + other.terms)
        else:
            return Expression(self.terms + [other])

    def __repr__(self):
        return " + ".join(str(term) for term in self.terms)
