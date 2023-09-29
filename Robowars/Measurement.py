
import numpy as np

import sys
import os
filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{filePath}\\..')

from CustomObjs.SensorFuncs import IMUFuncs
from Robowars.DynamicModel import DynamicModel

class MeasurementModel:
    def __init__(self):
        sigma_r = 0.015*np.sqrt(1.1e3)*np.pi/180 # Calculated from datasheet
        sigma_r = 2e0 # Guessing
        sigma_a = 230e-6*np.sqrt(1.125e3) # From datasheet
        sigma_a = 2e0 # Guessing
        self.Rv = np.eye(6)
        self.Rv[:3, :] *= sigma_a**2
        self.Rv[3:, :] *= sigma_r**2

    def h(self, x):
        return np.eye(6)@x
    
    def H(self, x):
        return np.eye(6)


class Filter:

    def __init__(self, dt, x0, P0):
        
        self.IMUFuncs = IMUFuncs()
        self.dynamicModel = DynamicModel(dt)
        self.measurementModel = MeasurementModel()

        self.x = x0 # Init state
        self.P = P0 # Init covariance matrix

        self.f = self.dynamicModel.f
        self.F = self.dynamicModel.F

        self.h = self.measurementModel.h
        self.H = self.measurementModel.H

        self.Qw = self.dynamicModel.Qw
        self.Rv = self.measurementModel.Rv
    
    def sample(self, u, data):
        gyro = data['gyro']

        r, p, y = self.IMUFuncs.getAngles(data)

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
        P_ = F@P@F.T + Qw

        # Predicted measurements
        H = self.H(x_)
        h = self.h(x_)

        # Compute Kalman gain
        K = P_@H.T@np.linalg.inv(H@P_@H.T + Rv)

        # Update state and covariance matrix
        x = x_ + K@(y - h)
        P = (np.eye(len(x)) - K@H)@P_@(np.eye(len(x)) - K@H).T + K@Rv@K.T

        return x, P
