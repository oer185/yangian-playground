from algebra.rewrite import Atom, Sum, Tensor, Coproduct, A


def parse_generator_name(name: str):
    """
    Expected format: TypeIndex_Level e.g. 'E1_0', 'E1_1', 'H1_2', 'F3_0'.
    Returns (typ, idx, level) as strings, or None if not parseable.
    """
    try:
        type_and_index, level = name.split("_")
        typ = type_and_index[0]  # 'E' / 'F' / 'H'
        idx = type_and_index[1:]  # e.g. '1'
        return typ, idx, level
    except Exception:
        return None


def coproduct_expand(atom: Atom):
    """
    Expand Δ for 1, and for generators E_i, F_i, H_i at levels 0/1/2.
    Always returns a Tensor or a Sum of Tensors (never a symbolic Coproduct)
    so tests can see '⊗' in repr().
    """
    name = atom.name

    # Unit
    if name == "1":
        # Δ(1) = 1 ⊗ 1
        return Tensor(Atom("1"), Atom("1"))

    parsed = parse_generator_name(name)
    if parsed is None:
        # Unknown atom: treat as primitive (level-0-like)
        return Sum([Tensor(atom, Atom("1")), Tensor(Atom("1"), atom)])

    typ, idx, level = parsed
    level = int(level)

    # Level-0: primitive coproduct
    if level == 0:
        return Sum([Tensor(atom, Atom("1")), Tensor(Atom("1"), atom)])

    # Level-1 (primitive):
    #   Δ(X^{(1)}) = X^{(1)} ⊗ 1 + 1 ⊗ X^{(1)}
    if level == 1:
        return Sum([Tensor(atom, Atom("1")), Tensor(Atom("1"), atom)])

    # Level-2 (minimal symmetric correction for E-type only):
    #   Δ(E^{(2)}) = E^{(2)}⊗1 + 1⊗E^{(2)}
    #                + E^{(1)}⊗H^{(0)} + H^{(0)}⊗E^{(1)}
    if level == 2:
        pieces = [Tensor(atom, Atom("1")), Tensor(Atom("1"), atom)]
        if typ == "E":
            pieces.append(Tensor(Atom(f"E{idx}_1"), Atom(f"H{idx}_0")))
            pieces.append(Tensor(Atom(f"H{idx}_0"), Atom(f"E{idx}_1")))
        return Sum(pieces)

    # Higher levels not implemented
    return Sum([Tensor(atom, Atom("1")), Tensor(Atom("1"), atom)])


def _expand_sum(parts):
    flat = []
    for p in parts:
        if isinstance(p, Sum):
            flat.extend(p.terms)
        else:
            flat.append(p)
    return Sum(flat) if len(flat) > 1 else (flat[0] if flat else Sum([]))


def _tensor_factors(expr):
    if isinstance(expr, Tensor):
        return _tensor_factors(expr.left) + _tensor_factors(expr.right)
    return [expr]


def _make_left_assoc(factors):
    cur = factors[0]
    for f in factors[1:]:
        cur = Tensor(cur, f)
    return cur


def _canonicalize_tensor_left(expr):
    if isinstance(expr, Sum):
        return Sum([_canonicalize_tensor_left(t) for t in expr.terms])
    if isinstance(expr, Tensor):
        return _make_left_assoc(_tensor_factors(expr))
    return expr


def _canonicalize_sum(expr):
    """Recursively sort Sum terms by repr for stable equality under repr()."""
    if isinstance(expr, Sum):
        items = [_canonicalize_sum(t) for t in expr.terms]
        items.sort(key=repr)
        return Sum(items)
    if isinstance(expr, Tensor):
        return Tensor(_canonicalize_sum(expr.left), _canonicalize_sum(expr.right))
    return expr


def apply_id_otimes_delta(expr):
    """
    (id ⊗ Δ)(expr): expand Δ on the right tensor leg recursively.
    """
    if isinstance(expr, Sum):
        return _expand_sum([apply_id_otimes_delta(t) for t in expr.terms])

    if isinstance(expr, Tensor):
        left = expr.left
        right = expr.right
        exp_right = coproduct_expand(right) if isinstance(right, Atom) else right
        if isinstance(exp_right, Sum):
            return _expand_sum([Tensor(left, term) for term in exp_right.terms])
        if isinstance(exp_right, Tensor):
            return Tensor(left, exp_right)
        return Tensor(left, exp_right)

    # If not a Tensor/Sum, try to expand if it's an Atom (rare in tests)
    if isinstance(expr, Atom):
        return apply_id_otimes_delta(coproduct_expand(expr))
    return expr


def apply_delta_otimes_id(expr):
    """
    (Δ ⊗ id)(expr): expand Δ on the left tensor leg recursively.
    """
    if isinstance(expr, Sum):
        return _expand_sum([apply_delta_otimes_id(t) for t in expr.terms])

    if isinstance(expr, Tensor):
        left = expr.left
        right = expr.right
        exp_left = coproduct_expand(left) if isinstance(left, Atom) else left
        if isinstance(exp_left, Sum):
            return _expand_sum([Tensor(term, right) for term in exp_left.terms])
        if isinstance(exp_left, Tensor):
            return Tensor(exp_left, right)
        return Tensor(exp_left, right)

    if isinstance(expr, Atom):
        return apply_delta_otimes_id(coproduct_expand(expr))
    return expr


def delta(atom: Atom):
    """
    Force an *expanded* coproduct (Tensor / Sum of Tensors), never Coproduct(...).
    """
    return coproduct_expand(atom)


def delta_associative_left(atom: Atom):
    out = apply_id_otimes_delta(delta(atom))
    out = _canonicalize_tensor_left(out)
    out = _canonicalize_sum(out)
    return out


def delta_associative_right(atom: Atom):
    out = apply_delta_otimes_id(delta(atom))
    out = _canonicalize_tensor_left(out)
    out = _canonicalize_sum(out)
    return out
