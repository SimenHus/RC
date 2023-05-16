# from supportingModules.MotorDriver import DCMotor
from time import sleep
import threading
import numpy as np

class ThrustAllocator(threading.Thread):

    def __init__(self, queue):
        super().__init__(name='Thrust')

        # Motor driver initialization
        motorRightPins = [12, 16] # Dummy pins
        motorLeftPins = [22, 10] # Dummy pins
        # self.MotorR = DCMotor(motorRightPins)
        # self.MotorL = DCMotor(motorLeftPins)
        # self.Motors = [self.MotorR, self.MotorL]


        self.desiredForces = {
            'force': np.array([0]*3),
            'torque': np.array([0]*3),
        }

        # Threading variables
        self.queue = queue
        self.daemon = True
        self.running = True

    def run(self):
        
        print('Thruster ready...')
        while self.running:
            if not self.queue.empty(): self.readmsg(self.queue.get())

    def allocateThrust(self, desiredForces):
        r = 1 # Dist from CoG to motor
        motor1Torque = (desiredForces['force'][1] + desiredForces['torque'][2]/r)/2
        motor2Torque = -(desiredForces['force'][1] - desiredForces['torque'][2]/r)/2

        Kt = 10 # Relation between motor voltage and torque
        v1 = motor1Torque/Kt
        v2 = motor2Torque/Kt

        print(f'\n\n--- Motor 1 ----- Motor 2 ---')
        print(f'--- {v1} ----- {v2} ---')

    def readmsg(self, msg):
        action, value, comment = msg
        if action == 'forces':
            self.desiredForces[comment] = value
            self.allocateThrust(self.desiredForces)

    def cleanup(self):
        # for motor in self.Motors: motor.cleanup()
        self.running = False


