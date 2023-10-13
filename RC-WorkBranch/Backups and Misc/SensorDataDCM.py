# Module to read and return sensor data

# import adafruit_bno055 # https://docs.circuitpython.org/projects/bno055/en/latest/
# import board # CircuitPython library
import numpy as np
import sympy as sp


class SensorData:
    'Module to collect and return sensor data'

    def __init__(self, dt):
        # i2c = board.I2C()
        # self.IMU = adafruit_bno055.BNO055_I2C(i2c)

        m = 4  # Total mass of disc
        discR = 1  # Radius of disc
        Jc = sp.eye(3)*1/2*m*discR  # Inertia of disc

        self.modelParams = [m, Jc]

        nx = 21 # Number of states
        self.nx = nx
        nu = 6 # Number of inputs
        self.xSymb = sp.symbols(f'x1:{nx+1}') # State vector symbolic
        self.uSymb = sp.symbols(f'u1:{nu+1}') # Input vector symbolic
        self.dt = dt # Sample time

        R0 = np.eye(3).reshape(9,)
        self.x = np.hstack((np.array([0]*12), R0)) # Initialize x
        self.P = np.eye(nx)*0.1 # Initialize P

        self.Q = np.eye(nx)  # Process noise
        self.R = np.eye(nx)  # Measurement noise (may not be Inxn matrix)

        self.f = sp.lambdify([self.xSymb, self.uSymb], self.stateFunc(), modules='numpy') # State function
        self.F = sp.lambdify([self.xSymb, self.uSymb], self.stateFunc().jacobian(self.xSymb), modules='numpy') # State funcion jacobian
        self.h = sp.lambdify([self.xSymb], self.measurementFunc(), modules='numpy') # Measurement function
        self.H = sp.lambdify([self.xSymb], self.measurementFunc().jacobian(self.xSymb), modules='numpy') # Measurement function jacobian

        self.Inxn = np.eye(nx)

        self.observability()


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
        roll = np.arctan2(accRaw[1], np.sqrt(accRaw[0]**2 + accRaw[2]**2))
        pitch = np.arctan2(accRaw[0], np.sqrt(accRaw[1]**2 + accRaw[2]**2))
        # Assuming IMU in CoG

        mag_x = magRaw[0]*np.cos(pitch) + magRaw[1]*np.sin(roll) * \
            np.sin(pitch) + magRaw[2]*np.cos(roll)*np.sin(pitch)
        mag_y = magRaw[1]*np.cos(roll) - magRaw[2]*np.sin(roll)
        yaw = np.arctan2(-mag_y, mag_x)

        measuredTheta = np.array([roll, pitch, yaw])

        y = np.hstack((measuredTheta, gyroRaw, accRaw*self.dt))


        # ------EKF algorithm----------
        # Get previous state
        x = self.x
        P = self.P

        # Predict
        F = self.F(x, u)
        x_ = self.f(x, u)
        P_ = F@P@F.T + self.Q

        # Predicted measurements
        H = self.H(x_)
        h = self.h(x_)

        # Compute Kalman gain
        K = P_@H.T@np.linalg.inv(H@P_@H.T + self.R)


        # Update state and covariance matrix
        x = x_ + K@(y - h)
        self.P = (self.Inxn - K@H)@P_@(self.Inxn - K@H).T + K@self.R@K.T

        self.x = x
        state = {
            'x': x[:3],
            'theta': x[3:6],
            'v': x[6:9],
            'w': x[9:12],
            'R': x[12:].reshape(3, 3),
        }

        return state
    
    def observability(self):
        R0 = np.eye(3).reshape(9,)
        x = np.hstack((np.array([3]*12), R0)) # Initialize x
        H = self.H(x)
        A = self.F(x, np.array([0]*6))
        O = self.H(x)

        obs = H
        for i in range(1, self.nx):
            obs = obs@A
            O = np.vstack((O, obs))

        print(np.linalg.matrix_rank(O))
        
    
    def stateFunc(self):
        rc = sp.Matrix(self.xSymb[:3])  # Position of body frame
        theta = sp.Matrix(self.xSymb[3:6])  # Orientation of body frame
        vc = sp.Matrix(self.xSymb[6:9])  # Velocity in body frame
        # Angular velocity in body frame according to inertial frame
        wia = sp.Matrix(self.xSymb[9:12])
        Ra = sp.Matrix(self.xSymb[12:]).reshape(3, 3)  # Rotation matrix from body to inertial
        m, Jc = self.modelParams

        F = sp.Matrix(self.uSymb[:3])
        T = sp.Matrix(self.uSymb[3:])

        rcDot = Ra*vc
        thetaDot = Ra*wia
        vcDot = -self.skew(wia)*vc + F/m
        wiaDot = Jc.inv()*(T - self.skew(wia)*Jc*wia)
        RaDot = Ra*self.skew(wia)

        # Euler discretization
        rcNext = rc + rcDot*self.dt
        thetaNext = theta + thetaDot*self.dt
        vcNext = vc + vcDot*self.dt
        wiaNext = wia + wiaDot*self.dt
        RaNext = (Ra*RaDot*self.dt).reshape(9, 1) # This is wrong
        
        return sp.Matrix.hstack(rcNext.T, thetaNext.T, vcNext.T, wiaNext.T, RaNext.T)

    def measurementFunc(self):
        nx = self.nx
        theta = sp.Matrix.zeros(3, nx)
        vc = sp.Matrix.zeros(3, nx)
        wia = sp.Matrix.zeros(3, nx)

        theta[:, 3:6] = sp.Matrix.eye(3)
        vc[:, 6:9] = sp.Matrix.eye(3)
        wia[:, 9:12] = sp.Matrix.eye(3)

        H = sp.Matrix.vstack(theta, vc, wia)

        return H*sp.Matrix(self.xSymb)

    def skew(self, vector):
        skewMatrix = sp.Matrix([
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0]
        ])
        return skewMatrix


app = SensorData(1)