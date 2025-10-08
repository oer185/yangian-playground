import pytest
from algebra.rewrite import *


def test_wildcard_matching_and_substitution():
    x = A('x')
    y = A('y')
    pat = Commutator(W('a'), Sum([W('b'), W('c')]))
    expr = Commutator(x, Sum([y, x]))
    env = match(pat, expr)
    assert env is not None
    assert env['a'] == x
    assert env['b'] == y
    assert env['c'] == x


def test_commutator_linearity_and_antisymmetry():
    e = A('e')
    f = A('f')
    h = A('h')
    expr = Commutator(h, Sum([e, f]))
    out = default_rewriter.normalize(expr)
    # expect two terms, possibly with -1 factors due to canonical ordering
    assert isinstance(out, Sum)
    assert len(out.terms) == 2
    terms_repr = [repr(t) for t in out.terms]
    # should contain canonical commutators of e,h and f,h
    assert any("[e,h]" in s for s in terms_repr)
    assert any("[f,h]" in s for s in terms_repr)


def test_rule_application_deep():
    e = A('e')
    f = A('f')
    h = A('h')
    nested = Commutator(Sum([h, e]), Sum([f, h]))
    # normalize should distribute both sides
    out = default_rewriter.normalize(nested)
    # result should be Sum of 4 commutators
    assert isinstance(out, Sum)
    assert len(out.terms) == 4


def test_coproduct_coassociativity_like_structure():
    x = A('x')
    expr = Coproduct(x)
    # with no rules, normalize is identity
    out = default_rewriter.normalize(expr)
    assert out == expr
