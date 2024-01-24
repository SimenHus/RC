# Module to read and return sensor data

import numpy as np
import sympy as sp

import sys
import os
filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{filePath}\\..')

from CustomObjs.SensorFuncs import IMUFuncs

class SensorData:
    'Module to collect and return sensor data'

    def __init__(self, dt, model, x0):
        
        self.IMU = IMUFuncs()
        self.model = model(dt, x0)

        self.nx = len(self.model.x0)

        self.x = self.model.x0 # Init state
        self.P = self.model.P0 # Init covariance matrix
        self.Qw = self.model.Qw # Get process noise
        self.Rv = self.model.Rv # Get measurement noise

        self.f = sp.lambdify([self.model.xSymb, self.model.uSymb],
                             self.model.f(), modules='numpy')  # State function
        self.F = sp.lambdify([self.model.xSymb, self.model.uSymb],
                             self.model.F(), modules='numpy')  # State funcion jacobian
        
    def h(self, x):
        return np.eye(6)@x
    
    def H(self, x):
        return np.eye(6)
    
    def sample(self, u, data):
        gyro = data['gyro']
        # If IMU is not in the CoG, transformation needs to be done

        r, p, y = self.IMU.getAngles(data)

        # q, wRate
        y = np.hstack((r, p, y, gyro))
        self.x, self.P = self.EKF(self.x, self.P, y, u, self.Qw, self.Rv)

        state = {
            'q': self.x[:3],
            'w': self.x[3:],
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
        h = self.h(x_)

        # Compute Kalman gain
        K = P_@H.T@np.linalg.inv(H@P_@H.T + Rv)

        # Update state and covariance matrix
        x = x_ + K@(y - h)
        P = (np.eye(self.nx) - K@H)@P_@(np.eye(self.nx) - K@H).T + K@Rv@K.T

        return x, P
