import sys
import os
filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{filePath}\\..')

from CustomObjs.Euler import EulerAnglesSymb, EulerAngleStateJacobian

import sympy as sp
import numpy as np

def skew(vector):

    skewMatrix = sp.Matrix([
        [0, -vector[2], vector[1]],
        [vector[2], 0, -vector[0]],
        [-vector[1], vector[0], 0]
    ])
    return skewMatrix

m = 2.5  # Total mass of disc
discR = 0.05  # Radius of disc
J = sp.eye(3)*1/2*m*discR  # Inertia of disc
dt = 10e-3
xSymb = sp.symbols(f'x1:{7}')  # State vector symbolic

q = sp.Matrix(xSymb[:3])  # Orientation of body frame
w = sp.Matrix(xSymb[3:])  # Angular velocity in body frame

R = EulerAnglesSymb(q)
Rsymbdiff = sp.lambdify([q], (R*w).jacobian(q), modules='numpy')  # State funcion jacobian


qnew = np.array([0, 0, 0])
Rnumdiff = EulerAngleStateJacobian(qnew, w)
print(Rnumdiff)
print(Rsymbdiff(qnew))

# qDot = sp.simplify(R*w)
# wDot = sp.simplify(J.inv()*(-skew(w)*J*w))

# # Euler discretization
# qNext = sp.simplify(q + qDot*dt)
# wNext = sp.simplify(w + wDot*dt)

