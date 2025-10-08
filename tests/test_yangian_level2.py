import pytest
from algebra.rewrite import A
from algebra.yangian import delta, delta_associative_left, delta_associative_right


def test_level2_coproduct():
    e2 = A('E1_2')
    out = delta(e2)
    s = repr(out)
    # Should include linear pieces and level-1/level-0 mixed terms
    assert 'E1_2' in s
    assert 'E1_1' in s
    assert 'H1_1' in s or 'H1_0' in s


def test_level2_coassociativity():
    e2 = A('E1_2')
    left = delta_associative_left(e2)
    right = delta_associative_right(e2)
    # normalize textual reprs — they should match structurally in this simplified model
    assert repr(left) == repr(right)
