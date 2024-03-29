import numpy as np
import sympy as sp

import sys
import os
filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{filePath}\\..')

from CustomObjs.Euler import EulerAnglesSymb

class RobotModel:
    def __init__(self, dt, x0, P0=np.eye(6)):
        sigma_r = 0.015*np.sqrt(1.1e3)*np.pi/180 # Calculated from datasheet
        sigma_r = 2e0 # Guessing
        sigma_a = 230e-6*np.sqrt(1.125e3) # From datasheet
        sigma_a = 2e0 # Guessing
        self.Rv = np.eye(6)
        self.Rv[:3, :] *= sigma_a**2
        self.Rv[3:, :] *= sigma_r**2
        self.Qw = np.eye(6)*5e-3
        self.x0 = x0
        self.P0 = P0
        self.u0 = np.array([0]*6)
        m = 2.5  # Total mass of disc
        discR = 0.05  # Radius of disc
        Jc = sp.eye(3)*1/2*m*discR  # Inertia of disc
        self.params = [m, discR, Jc]
        self.dt = dt

        self.xSymb = sp.symbols(f'x1:{7}')  # State vector symbolic
        self.uSymb = sp.symbols(f'u1:{7}')  # Input vector symbolic
 
    def f(self):
        q = sp.Matrix(self.xSymb[:3])  # Orientation of body frame
        w = sp.Matrix(self.xSymb[3:])  # Angular velocity in body frame
        m, discR, J = self.params

        F = sp.Matrix(self.uSymb[:3])
        T = sp.Matrix(self.uSymb[3:])

        R = EulerAnglesSymb(q)
        qDot = sp.simplify(R*w)
        wDot = sp.simplify(J.inv()*(T - self.skew(w)*J*w))

        # Euler discretization
        qNext = sp.simplify(q + qDot*self.dt)
        wNext = sp.simplify(w + wDot*self.dt)

        return sp.Matrix.vstack(qNext, wNext)
    
    def F(self):
        return self.f().jacobian(self.xSymb)
    
    def skew(self, vector):

        skewMatrix = sp.Matrix([
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0]
        ])
        return skewMatrix
