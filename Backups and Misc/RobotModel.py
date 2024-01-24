import numpy as np
import sympy as sp

import os
filePath = os.path.dirname(os.path.abspath(__file__))

class RobotModel:
    def __init__(self, dt, x0, P0=np.eye(13)*0.1):
        with open(f'{filePath}\\sensordata\\Rv.npy', 'rb') as f:
            a = np.load(f)
        self.Rv = np.cov(a, rowvar=False)  # Measurement noise
        Qr, Qq, Qv, Qw = 5e0, 5e-1, 5e0, 5e-1
        self.Qw = np.eye(13) # Process noise
        self.Qw[:3, :3] *= Qr
        self.Qw[3:7, 3:7] *= Qq
        self.Qw[7:10, 7:10] *= Qv
        self.Qw[10:13, 10:13] *= Qw
        self.x0 = x0
        self.P0 = P0
        self.u0 = np.array([0]*6)
        m = 2.5  # Total mass of disc
        discR = 0.05  # Radius of disc
        Jc = sp.eye(3)*1/2*m*discR  # Inertia of disc
        self.params = [m, discR, Jc]
        self.dt = dt
        self.nx = len(self.x0)

        self.xSymb = sp.symbols(f'x1:{14}')  # State vector symbolic
        self.uSymb = sp.symbols(f'u1:{7}')  # Input vector symbolic
 
    def stateFunc(self):
        r = sp.Matrix(self.xSymb[:3])  # Position of body frame
        q = sp.Matrix(self.xSymb[3:7])  # Orientation of body frame
        v = sp.Matrix(self.xSymb[7:10])  # Velocity in body frame
        w = sp.Matrix(self.xSymb[10:13])  # Angular velocity in body frame
        m, discR, J = self.params

        F = sp.Matrix(self.uSymb[:3])
        T = sp.Matrix(self.uSymb[3:])

        nu, e1, e2, e3 = q
        eps = sp.Matrix(q[1:])

        R = sp.Matrix([
            [nu**2 + e1**2 - e2**2 - e3**2, 2 *
                (e1*e2 - nu*e3), 2*(e1*e3 + nu*e2)],
            [2*(e1*e2 + nu*e3), nu**2 - e1**2 +
                e2**2 - e3**2, 2*(e2*e3 - nu*e1)],
            [2*(e1*e3 - nu*e2), 2*(e2*e3 + nu*e1), nu**2 - e1**2 - e2**2 + e3**2]
        ])

        U = sp.Matrix.vstack(
            -eps.T,
            nu*sp.eye(3) + self.skew(eps)
        )

        def quaternionMultiplication(q1, q2):
            nu1 = sp.Matrix([q1[0]])
            eps1 = sp.Matrix(q1[1:])
            nu2 = sp.Matrix([q2[0]])
            eps2 = sp.Matrix(q2[1:])

            m1 = sp.Matrix.vstack(
                sp.Matrix.hstack(nu1, -eps1.T),
                sp.Matrix.hstack(eps1.reshape(3, 1), nu1[0]*sp.Matrix.eye(3) + self.skew(eps1))
            )
            m2 = sp.Matrix.vstack(nu2, eps2)
            return m1*m2

        def qFromAngleAxis(axis, angle):
            return sp.Matrix.vstack(sp.Matrix([sp.cos(angle/2)]), axis*sp.sin(angle/2)) # See https://hal.science/hal-01122406/document (101)

        normW = sp.sqrt(w[0]**2 + w[1]**2 + w[2]**2)
        rDot = sp.simplify(R*v)
        qDot = sp.simplify(1/2*U*w) # See https://hal.science/hal-01122406/document (227)
        vDot = sp.simplify(-self.skew(w)*v + F/m)
        wDot = sp.simplify(J.inv()*(T - self.skew(w)*J*w))

        # Euler discretization
        rNext = sp.simplify(r + rDot*self.dt)
        qNext = sp.simplify(q + qDot*self.dt) # See https://hal.science/hal-01122406/document (227)
        vNext = sp.simplify(v + vDot*self.dt)
        wNext = sp.simplify(w + wDot*self.dt)

        return sp.Matrix.vstack(rNext, qNext, vNext, wNext)

    def measurementFunc(self):
        q = sp.Matrix.zeros(4, self.nx)
        # v = sp.Matrix.zeros(3, self.nx)
        w = sp.Matrix.zeros(3, self.nx)

        q[:, 3:7] = sp.Matrix.eye(4)
        # v[:, 7:10] = sp.Matrix.eye(3)
        w[:, 10:13] = sp.Matrix.eye(3)

        H = sp.Matrix.vstack(q, w)

        return H*sp.Matrix(self.xSymb)

    def skew(self, vector):

        skewMatrix = sp.Matrix([
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0]
        ])
        return skewMatrix
