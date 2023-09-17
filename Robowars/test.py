import sympy as sp


r, p, y = sp.symbols('r p y')

Rx = sp.Matrix([
    [sp.cos(r), -sp.sin(r), 0],
    [sp.sin(r), sp.cos(r), 0],
    [0, 0, 1]
])

Ry = sp.Matrix([
    [sp.cos(p), 0, sp.sin(p)],
    [0, 1, 0],
    [-sp.sin(p), 0, sp.cos(p)]
])

Rz = sp.Matrix([
    [1, 0, 0],
    [0, sp.cos(y), -sp.sin(y)],
    [0, sp.sin(y), sp.cos(y)]
])