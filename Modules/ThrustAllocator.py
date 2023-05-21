# from supportingModules.MotorDriver import DCMotor
from time import sleep, time
import threading
import numpy as np

class ThrustAllocator(threading.Thread):

    def __init__(self):
        super().__init__(name='Thrust')

        # Motor driver initialization
        motorRightPins = [12, 16] # Dummy pins
        motorLeftPins = [22, 10] # Dummy pins
        # self.MotorR = DCMotor(motorRightPins)
        # self.MotorL = DCMotor(motorLeftPins)
        # self.Motors = [self.MotorR, self.MotorL]

        self.idle = True # If motors should remain idle

        self.dState = {
            'pos': np.array([0]*3),
            'angle': np.array([0]*3),
            'linVel': np.array([0]*3),
            'angVel': np.array([0]*3),
        }

        self.state = {
            'x': np.array([0]*3),
            'theta': np.array([0]*3),
            'v': np.array([0]*3),
            'w': np.array([0]*3),
        }

        self.R = self.getR(np.array([0]*3)) # Rotational matrix (euler angles)

        # Controller params
        self.Kpx = 1 # Gain linear Kp
        self.Kptheta = 0.1 # Gain angular Kp
        self.Kdc = 4 # Gain all Kd
        self.T = 1000 # Sample time in ms

        # Motor params
        self.Kf = 1 # Motor force const
        self.fd = 0 # Linear friction
        self.td = 0 # Rotational friction
        
        # System params
        self.rw = 1 # Dist from CoG to wheel

        # Threading variables
        self.daemon = True
        self.running = True

    def run(self):
        
        print('Thrusters ready...')
        while self.running:
            startTime = time()
            if self.idle:
                # for motor in self.Motors: motor.setIdle()
                sleep(1)
                continue

            tau = self.controller(self.state, self.dState)

            # Motor calculations
            Vs = (tau[5] + self.td)/(self.Kf*self.rw)
            Vd = (tau[1] + self.fd)/self.Kf

            V1 = 1/2*(Vs + Vd)
            V2 = 1/2*(Vs - Vd)

            print(f'\n\n--- Motor 1 ----- Motor 2 ---')
            print(f'--- {V1} ----- {V2} ---')
            
            sleepTime = (self.T - (time() - startTime)) / 1000 # Sleep time in ms
            if sleepTime < 0: sleepTime = 0
            sleep(sleepTime)

    def changeSetpoint(self, pos=None, angle=None, linVel=None, angVel=None):
        if linVel is not None: self.dState['linVel'] = self.R.T@linVel
        if angVel is not None: self.dState['angVel'] = angVel
        self.idle = False # Only for testing purposes, should be removed

    def updateState(self, state):
        self.state = state
        self.R = self.getR(state['theta'])
            

    def getR(self, theta):
        c1 = np.cos(theta[0] * np.pi / 180)
        s1 = np.sin(theta[0] * np.pi / 180)
        c2 = np.cos(theta[1] * np.pi / 180)
        s2 = np.sin(theta[1] * np.pi / 180)
        c3 = np.cos(theta[2] * np.pi / 180)
        s3 = np.sin(theta[2] * np.pi / 180)

        matrix = np.array([[c2*c3, -c2*s3, s2],
                           [c1*s3+c3*s1*s2, c1*c3-s1*s2*s3, -c2*s1],
                           [s1*s3-c1*c3*s2, c3*s1+c1*s2*s3, c1*c2]])
        return matrix

    def controller(self, state, dState):
        z = np.hstack((state['x'], state['theta']))
        nu = np.hstack((state['v'], state['w']))
        zd = np.hstack((dState['pos'], dState['angle']))
        nud = np.hstack((dState['linVel'], dState['angVel']))

        zTilde = z - zd
        nuTilde = nu - nud
        Kp = self.Kp()
        Kd = self.Kd()
        tau = -Kd@nuTilde - Kp@zTilde

        return tau

    def Kp(self):
        I3x3 = np.diag([1]*3)
        return np.vstack((np.hstack((self.R.T@I3x3*self.Kpx, np.zeros((3, 3)))),
                          np.hstack((np.zeros((3, 3)), self.R.T@I3x3*self.Kptheta))))
    
    def Kd(self):
        return np.diag([1]*6)*self.Kdc

    def cleanup(self):
        # for motor in self.Motors: motor.cleanup()
        self.idle = True
        self.running = False


