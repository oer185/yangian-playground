import pytest
from algebra.rewrite import A
from algebra.yangian import delta, delta_associative_left, delta_associative_right, parse_generator_name


def test_parse_generator_name():
    assert parse_generator_name('E1_1') == ('E', '1', '1')
    assert parse_generator_name('F2_1') == ('F', '2', '1')
    assert parse_generator_name('H3_1') == ('H', '3', '1')
    assert parse_generator_name('not_a_gen') is None


def test_coproduct_expansion_level1():
    e1 = A('E1_1')
    out = delta(e1)
    # Expect Δ(E1_1) = E1_1 ⊗ 1 + 1 ⊗ E1_1
    s = repr(out)
    assert '⊗' in s
    assert 'E1_1' in s


def test_coproduct_coassociativity_level1():
    e1 = A('E1_1')
    left = delta_associative_left(e1)
    right = delta_associative_right(e1)
    # For this simple expansion both should produce a Sum of 4 tensor products
    assert repr(left) == repr(right)
    s = repr(left)
    # there should be at least two triple-tensor terms (each contributes 2 '⊗')
    assert s.count('⊗') >= 4
