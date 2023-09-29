import numpy as np

import sys
import os
filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{filePath}\\..')

from CustomObjs.Euler import EulerAngles, EulerAngleStateJacobian

class DynamicModel:
    def __init__(self, dt):
        self.Qw = np.eye(6)*5e-3 # Process noise
        m = 2.5  # Total mass of disc
        discR = 0.05  # Radius of disc
        J = np.eye(3)*1/2*m*discR # Inertia of disc
        self.params = [m, discR, J, np.linalg.inv(J)]
        self.dt = dt
    
    def f(self, x, u):
        q = x[:3]
        w = x[3:]
        m, discR, J, Jinv = self.params

        F = u[:3]
        T = u[3:]

        R = EulerAngles(q)
        qDot = R@w
        wDot = Jinv@(T - self.skew(w)@J@w)

        return np.hstack((q + qDot*self.dt, w + wDot*self.dt))

    def F(self, x, u):
        q = x[:3]
        w = x[3:]
        R = EulerAngles(q)
        m, discR, J, Jinv = self.params
        i, k, j = np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])
        Jw = J@w
        skewWJ = self.skew(w)@J

        Jqq = np.eye(3) + EulerAngleStateJacobian(q, w)*self.dt
        Jqw = np.hstack((R[:, 0].reshape((3,1)), R[:, 1].reshape((3,1)), R[:, 2].reshape((3,1))))*self.dt
        Jwq = np.zeros((3, 3))
        Jww = np.eye(3) + Jinv@np.hstack((
            (- self.skew(i)@Jw - skewWJ[:, 0]).reshape((3, 1)),
            (- self.skew(j)@Jw - skewWJ[:, 1]).reshape((3, 1)),
            (- self.skew(k)@Jw - skewWJ[:, 2]).reshape((3, 1))
        ))*self.dt

        J = np.vstack((
            np.hstack((Jqq, Jqw)),
            np.hstack((Jwq, Jww))
        ))

        return J
    
    def skew(self, vector):

        skewMatrix = np.array([
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0]
        ])
        return skewMatrix
