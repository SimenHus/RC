# Module to read and return sensor data

import adafruit_bno055 # https://docs.circuitpython.org/projects/bno055/en/latest/
import board # CircuitPython library
import numpy as np


class SensorData:
    'Module to collect and return sensor data'

    def __init__(self):
        i2c = board.I2C()
        self.IMU = adafruit_bno055.BNO055_I2C(i2c)
        
        self.A = np.array([
            [1, 0],
            [0, 1],
        ])
        self.B = np.array([
            [1],
            [0],
        ])
        self.C = np.array([0, 0])
        self.D = np.array([0])

        self.Rv = np.array([0])

        self.x_apriori = np.array([0])
        self.P_apriori = np.array([0])


    def sample(self): # Sample filter or sumfn
        accRaw = self.IMU.acceleration # Raw acceleration reading, includes gravity + lin acc
        gyroRaw = self.IMU.gyro # rad/s
        euler = self.IMU.euler # rad
        linAcc = self.IMU.linear_acceleration # Raw acc - gravity
        gravity = self.IMU.gravity # Gravity vector

        # May use IMUPLUS_MODE or ACCGYRO_MODE to improve data output rate
        # If kalman filter is used, only raw data is necessary from the sensor and the output rate can be high
        y = np.array([0])

        # EKF algorithm
        L = self.P_apriori@self.C.T@np.linalg.inv(self.C@self.P_apriori + self.Rv)
        x = self.x_apriori + L@(y - self.C@self.x_apriori)

