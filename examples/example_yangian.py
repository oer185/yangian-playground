if False:
    # (this block is not executed when imported; copy into repo/tests to run)
    from algebra.rewrite import *
    # Define simple generators e,f,h
    e = A('e')
    f = A('f')
    h = A('h')
    # Example commutator [h, e+f]
    expr = Commutator(h, Sum([e, f]))
    print('before:', expr)
    print('after :', default_rewriter.normalize(expr))