# Module to read and return sensor data

import numpy as np
import sympy as sp

import sys
import os
filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{filePath}\\..')
from CustomObjs.Quaternion import Quaternion

class SensorData:
    'Module to collect and return sensor data'

    def __init__(self, dt, model, x0):
        
        self.model = model(dt, x0)

        self.nx = len(self.model.x0)

        self.x = self.model.x0 # Init state
        self.P = self.model.P0 # Init covariance matrix
        self.Qw = self.model.Qw # Get process noise
        self.Rv = self.model.Rv # Get measurement noise

        self.f = sp.lambdify([self.model.xSymb, self.model.uSymb],
                             self.model.stateFunc(), modules='numpy')  # State function
        self.F = sp.lambdify([self.model.xSymb, self.model.uSymb], self.model.stateFunc().jacobian(
            self.model.xSymb), modules='numpy')  # State funcion jacobian
        # Measurement function
        self.h = sp.lambdify(
            [self.model.xSymb], self.model.measurementFunc(), modules='numpy')
        self.H = sp.lambdify([self.model.xSymb], self.model.measurementFunc().jacobian(
            self.model.xSymb), modules='numpy')  # Measurement function jacobian
        

    def sample(self, u, data):
        accRaw = data['acc']
        magRaw = data['mag']
        gyroRaw = data['gyro']
        # If IMU is not in the CoG, transformation needs to be done

        qObj = Quaternion()
        qAcc = qObj.qAcc(accRaw)
        qMag = qObj.qMag(qAcc, magRaw)

        qMeasured = qMag*qAcc
        qMeasured.normalize()

        # q, wRate
        y = np.hstack((qMeasured.q(), gyroRaw))
        self.x, self.P = self.EKF(self.x, self.P, y, u, self.Qw, self.Rv)
        q = Quaternion(self.x[3:7])
        q.normalize()
        self.x[3:7] = q.q()

        state = {
            'x': self.x[:3],
            'q': q,
            'v': self.x[7:10],
            'w': self.x[10:13],
            'R': q.toRotationMatrix(),
            'euler': q.toRPY()
        }

        return state
    
    def EKF(self, x, P, y, u, Qw, Rv):
        # ------EKF algorithm----------

        # Predict
        F = self.F(x, u)
        x_ = self.f(x, u)
        x_ = x_.reshape((x_.shape[0],))
        P_ = F@P@F.T + Qw

        # Predicted measurements
        H = self.H(x_)
        h = self.h(x_)[:, 0]
        h = h.reshape((h.shape[0],))

        # Compute Kalman gain
        K = P_@H.T@np.linalg.inv(H@P_@H.T + Rv)

        # Update state and covariance matrix
        x = x_ + K@(y - h)
        P = (np.eye(self.nx) - K@H)@P_@(np.eye(self.nx) - K@H).T + K@Rv@K.T

        return x, P

    def observability(self):
        x = self.x
        H = self.H(x)
        A = self.F(x, np.array([0]*6))
        O = self.H(x)

        obs = H
        for i in range(1, self.nx):
            obs = obs@A
            O = np.vstack((O, obs))

        print('Shape: ', O.shape)
        print('Rank: ', np.linalg.matrix_rank(O))