import sympy as sp

tings = sp.Matrix([1, 0])

print(sp.Matrix.hstack(tings.T, [1]))
