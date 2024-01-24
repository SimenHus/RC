# Module to read and return sensor data

import adafruit_bno055 # https://docs.circuitpython.org/projects/bno055/en/latest/
import board # CircuitPython library
import numpy as np
import sympy as sp


class BNO055Interface:
    'Module to read BNO055 sensor data'

    def __init__(self, dt):
        i2c = board.I2C()
        # self.IMU = adafruit_bno055.BNO055_I2C(i2c)

        m = 4  # Total mass of disc
        discR = 1  # Radius of disc
        Jc = sp.eye(3)*1/2*m*discR  # Inertia of disc

        self.modelParams = [m, Jc]

        nx = 13 # Number of states
        self.nx = nx
        nu = 6 # Number of inputs
        self.xSymb = sp.symbols(f'x1:{nx+1}') # State vector symbolic
        self.uSymb = sp.symbols(f'u1:{nu+1}') # Input vector symbolic
        self.dt = dt # Sample time

        q0 = np.array([1, 0, 0, 0])
        self.x = np.hstack(([0]*3, q0, [0]*(nx-7))) # Initialize x
        self.P = np.eye(nx)*0.1 # Initialize P

        self.Qw = np.eye(nx)  # Process noise
        self.Rv = np.eye(nx)  # Measurement noise (may not be Inxn matrix)

        self.Inxn = np.eye(nx)
        self.I3x3 = np.eye(3)

        self.f = sp.lambdify([self.xSymb, self.uSymb], self.stateFunc(), modules='numpy') # State function
        self.F = sp.lambdify([self.xSymb, self.uSymb], self.stateFunc().jacobian(self.xSymb), modules='numpy') # State funcion jacobian
        self.h = sp.lambdify([self.xSymb], self.measurementFunc(), modules='numpy') # Measurement function
        self.H = sp.lambdify([self.xSymb], self.measurementFunc().jacobian(self.xSymb), modules='numpy') # Measurement function jacobian

        self.numR = sp.lambdify([self.xSymb[3:7]], self.R(self.xSymb[3:7]), modules='numpy')
        # self.observability() # Check observability of system


    def sample(self, u):
        # Read sensor data
        accRaw = np.array(self.IMU.acceleration) # Raw acceleration reading, includes gravity + lin acc
        gyroRaw = np.array(self.IMU.gyro) # Raw angular velocity rad/s
        magRaw = np.array(self.IMU.magnetic) # Raw readings from magnetometer in micro-tesla
        # euler = np.array(self.IMU.euler) # rad
        # linAcc = np.array(self.IMU.linear_acceleration) # Raw acc - gravity
        # gravity = np.array(self.IMU.gravity) # Gravity vector

        # If IMU is not in the CoG, transformation needs to be done

        # May use IMUPLUS_MODE or ACCGYRO_MODE to improve data output rate
        # If kalman filter is used, only raw data is necessary from the sensor and the output rate can be high

        # Convert sensor readings to y
        r = np.arctan2(accRaw[1], np.sqrt(accRaw[0]**2 + accRaw[2]**2))
        p = np.arctan2(accRaw[0], np.sqrt(accRaw[1]**2 + accRaw[2]**2))
        # Assuming IMU in CoG

        mag_x = magRaw[0]*np.cos(p) + magRaw[1]*np.sin(r) * \
            np.sin(p) + magRaw[2]*np.cos(r)*np.sin(p)
        mag_y = magRaw[1]*np.cos(r) - magRaw[2]*np.sin(r)
        y = np.arctan2(-mag_y, mag_x)

        c = lambda _: np.cos(_)
        s = lambda _: np.sin(_)

        # Euler angles to quaternions
        measuredQ = np.array([
            [c(r)*c(p)*c(y) + s(r)*s(p)*s(y)],
            [s(r)*c(p)*c(y) - c(r)*s(p)*s(y)],
            [c(r)*s(p)*c(y) + s(r)*c(p)*s(y)],
            [c(r)*c(p)*s(y) - s(r)*s(p)*c(y)],
        ])

        y = np.hstack((measuredQ, gyroRaw, accRaw*self.dt))


        # ------EKF algorithm----------
        # Get previous state
        x = self.x
        P = self.P

        # Predict
        F = self.F(x, u)
        x_ = self.f(x, u)
        x_[3:7] = x_[3:7]/np.linalg.norm(x_[3:7])
        P_ = F@P@F.T + self.Qw

        # Predicted measurements
        H = self.H(x_)
        h = self.h(x_)

        # Compute Kalman gain
        K = P_@H.T@np.linalg.inv(H@P_@H.T + self.Rv)


        # Update state and covariance matrix
        x = x_ + K@(y - h)
        self.P = (self.Inxn - K@H)@P_@(self.Inxn - K@H).T + K@self.Rv@K.T

        x[3:7] = x[3:7]/np.linalg.norm(x[3:7])
        self.x = x

        state = {
            'x': x[:3],
            'q': x[3:7],
            'v': x[7:10],
            'w': x[10:13],
            'R': self.numR(x[3:7]),
        }

        return state
    
    def observability(self):
        q0 = np.array([1, 0, 0, 0])
        x = np.hstack(([0]*3, q0, [0]*(self.nx-7)))  # Initialize x
        H = self.H(x)
        A = self.F(x, np.array([1]*6))
        O = self.H(x)

        obs = H
        for i in range(1, self.nx):
            obs = obs@A
            O = np.vstack((O, obs))

        print(np.linalg.matrix_rank(O))
        
    def R(self, q):
        nu, e1, e2, e3 = q

        R = sp.Matrix([
            [nu**2 + e1**2 - e2**2 - e3**2, 2*(e1*e2 - nu*e3), 2*(e1*e3 + nu*e2)],
            [2*(e1*e2 + nu*e3), nu**2 - e1**2 + e2**2 - e3**2, 2*(e2*e3 - nu*e1)],
            [2*(e1*e3 - nu*e2), 2*(e2*e3 + nu*e1), nu**2 - e1**2 - e2**2 + e3**2]
        ])

        return R
    
    def U(self, q):
        nu = q[0]
        eps = sp.Matrix(q[1:])
        U = sp.Matrix.vstack(
            -eps.T,
            nu*self.I3x3 + self.skew(eps)
        )
        return U

    
    def stateFunc(self):
        r = sp.Matrix(self.xSymb[:3])  # Position of body frame
        q = sp.Matrix(self.xSymb[3:7])  # Orientation of body frame
        v = sp.Matrix(self.xSymb[7:10])  # Velocity in body frame
        w = sp.Matrix(self.xSymb[10:13])  # Angular velocity in body frame
        m, J = self.modelParams

        F = sp.Matrix(self.uSymb[:3])
        T = sp.Matrix(self.uSymb[3:])

        R = self.R(q)
        U = self.U(q)

        rDot = sp.simplify(R*v)
        qDot = sp.simplify(1/2*U*w)
        vDot = sp.simplify(-self.skew(w)*v + F/m)
        wDot = sp.simplify(J.inv()*(T - self.skew(w)*J*w))

        # Euler discretization 
        rNext = sp.simplify(r + rDot*self.dt)
        qNext = sp.simplify(q + qDot*self.dt)
        vNext = sp.simplify(v + vDot*self.dt)
        wNext = sp.simplify(w + wDot*self.dt)

        return sp.Matrix.vstack(rNext, qNext, vNext, wNext)

    def measurementFunc(self):
        nx = self.nx
        q = sp.Matrix.zeros(4, nx)
        v = sp.Matrix.zeros(3, nx)
        w = sp.Matrix.zeros(3, nx)

        q[:, 3:7] = sp.Matrix.eye(4)
        v[:, 7:10] = sp.Matrix.eye(3)
        w[:, 10:13] = sp.Matrix.eye(3)

        H = sp.Matrix.vstack(q, v, w)

        return H*sp.Matrix(self.xSymb)

    def skew(self, vector):
        skewMatrix = sp.Matrix([
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0]
        ])
        return skewMatrix