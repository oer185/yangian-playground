from typing import Dict, List, Optional, Callable


class Expr:
    """Base expression class. Subclass for Atom (generators, symbols), Sum, Product, Commutator, Coproduct, Tensor."""

    def subs(self, mapping: Dict[str, 'Expr']) -> 'Expr':
        return self


class Atom(Expr):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name


class Sum(Expr):
    def __init__(self, terms: List[Expr]):
        # flatten
        flat: List[Expr] = []
        for t in terms:
            if isinstance(t, Sum):
                flat.extend(t.terms)
            else:
                flat.append(t)
        self.terms = flat

    def __repr__(self):
        return "(" + " + ".join(map(repr, self.terms)) + ")"

    def __eq__(self, other):
        return isinstance(other, Sum) and self.terms == other.terms


class Product(Expr):
    def __init__(self, factors: List[Expr]):
        flat: List[Expr] = []
        for f in factors:
            if isinstance(f, Product):
                flat.extend(f.factors)
            else:
                flat.append(f)
        self.factors = flat

    def __repr__(self):
        return "(" + " * ".join(map(repr, self.factors)) + ")"

    def __eq__(self, other):
        return isinstance(other, Product) and self.factors == other.factors


class Commutator(Expr):
    def __init__(self, a: Expr, b: Expr):
        self.a = a
        self.b = b

    def __repr__(self):
        return f"[{self.a},{self.b}]"

    def __eq__(self, other):
        return isinstance(other, Commutator) and self.a == other.a and self.b == other.b


class Coproduct(Expr):
    def __init__(self, a: Expr):
        self.a = a

    def __repr__(self):
        return f"Δ({self.a})"

    def __eq__(self, other):
        return isinstance(other, Coproduct) and self.a == other.a


class Tensor(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} ⊗ {self.right})"

    def __eq__(self, other):
        return isinstance(other, Tensor) and self.left == other.left and self.right == other.right


# Patterns and matching
class Wildcard(Expr):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"?{self.name}"


Match = Optional[Dict[str, Expr]]


def match(pattern: Expr, expr: Expr, env: Optional[Dict[str, Expr]] = None) -> Match:
    if env is None:
        env = {}
    # Wildcard matches
    if isinstance(pattern, Wildcard):
        prev = env.get(pattern.name)
        if prev is None:
            env[pattern.name] = expr
            return env
        else:
            return env if prev == expr else None
    # Match Atom
    if isinstance(pattern, Atom) and isinstance(expr, Atom):
        return env if pattern.name == expr.name else None
    if type(pattern) is type(expr):
        if isinstance(pattern, Sum):
            if len(pattern.terms) != len(expr.terms):
                return None
            for pterm, eterm in zip(pattern.terms, expr.terms):
                env = match(pterm, eterm, env)
                if env is None:
                    return None
            return env
        if isinstance(pattern, Product):
            if len(pattern.factors) != len(expr.factors):
                return None
            for pf, ef in zip(pattern.factors, expr.factors):
                env = match(pf, ef, env)
                if env is None:
                    return None
            return env
        if isinstance(pattern, Commutator):
            env = match(pattern.a, expr.a, env)
            if env is None: return None
            env = match(pattern.b, expr.b, env)
            return env
        if isinstance(pattern, Coproduct):
            return match(pattern.a, expr.a, env)
        if isinstance(pattern, Tensor):
            env = match(pattern.left, expr.left, env)
            if env is None: return None
            env = match(pattern.right, expr.right, env)
            return env
    return None


# Rewrites
class RewriteRule:
    def __init__(self, lhs: Expr, rhs_func: Callable[[Dict[str, Expr]], Expr]):
        self.lhs = lhs
        self.rhs_func = rhs_func

    def try_apply(self, expr: Expr) -> Optional[Expr]:
        env = match(self.lhs, expr)
        if env is not None:
            return self.rhs_func(env)
        # try deeper
        if isinstance(expr, Sum):
            new_terms = []
            changed = False
            for t in expr.terms:
                nt = self.try_apply(t)
                if nt is not None:
                    new_terms.append(nt)
                    changed = True
                else:
                    new_terms.append(t)
            if changed:
                return Sum(new_terms)
        if isinstance(expr, Product):
            new_factors = []
            changed = False
            for f in expr.factors:
                nf = self.try_apply(f)
                if nf is not None:
                    new_factors.append(nf)
                    changed = True
                else:
                    new_factors.append(f)
            if changed:
                return Product(new_factors)
        if isinstance(expr, Commutator):
            na = self.try_apply(expr.a)
            nb = self.try_apply(expr.b)
            if na is not None or nb is not None:
                return Commutator(na or expr.a, nb or expr.b)
        if isinstance(expr, Coproduct):
            na = self.try_apply(expr.a)
            if na is not None:
                return Coproduct(na)
        if isinstance(expr, Tensor):
            nla = self.try_apply(expr.left)
            nrb = self.try_apply(expr.right)
            if nla is not None or nrb is not None:
                return Tensor(nla or expr.left, nrb or expr.right)
        return None


class Rewriter:
    def __init__(self, rules: List[RewriteRule]):
        self.rules = rules

    def normalize(self, expr: Expr, max_iters=100) -> Expr:
        current = expr
        for i in range(max_iters):
            changed = False
            for r in self.rules:
                res = r.try_apply(current)
                if res is not None and res != current:
                    current = res
                    changed = True
                    break
            if not changed:
                return current
        return current


# Useful helpers to build rules more easily
def rule(lhs: Expr, rhs: Expr) -> RewriteRule:
    return RewriteRule(lhs, lambda env: substitute(rhs, env))


def substitute(expr: Expr, env: Dict[str, Expr]) -> Expr:
    if isinstance(expr, Wildcard):
        return env[expr.name]
    if isinstance(expr, Atom):
        return expr
    if isinstance(expr, Sum):
        return Sum([substitute(t, env) for t in expr.terms])
    if isinstance(expr, Product):
        return Product([substitute(f, env) for f in expr.factors])
    if isinstance(expr, Commutator):
        return Commutator(substitute(expr.a, env), substitute(expr.b, env))
    if isinstance(expr, Coproduct):
        return Coproduct(substitute(expr.a, env))
    if isinstance(expr, Tensor):
        return Tensor(substitute(expr.left, env), substitute(expr.right, env))
    return expr


# Simple algebraic helpers
A = lambda name: Atom(name)
W = lambda name: Wildcard(name)


# Example: define commutator linearity and antisymmetry
# We avoid infinite flipping by not applying antisymmetry if the LHS is already in lexicographic order.
def antisymmetry_rule():
    x, y = W("x"), W("y")

    def rhs(env):
        a, b = env["x"], env["y"]
        # enforce canonical ordering: only flip if repr(a) > repr(b)
        if repr(a) > repr(b):
            return Product([Atom("-1"), Commutator(b, a)])
        return Commutator(a, b)

    return RewriteRule(Commutator(x, y), rhs)


default_rules = [
    # linearity first
    RewriteRule(
        Commutator(W("x"), Sum([W("y"), W("z")])),
        lambda env: Sum([Commutator(env["x"], env["y"]), Commutator(env["x"], env["z"])])
    ),
    RewriteRule(
        Commutator(Sum([W("x"), W("y")]), W("z")),
        lambda env: Sum([Commutator(env["x"], env["z"]), Commutator(env["y"], env["z"])])
    ),
    antisymmetry_rule(),
]

default_rewriter = Rewriter(default_rules)
