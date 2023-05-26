# Native imports
from time import sleep, time
from queue import Queue
from threading import Thread
import numpy as np


# Custom modules
from Modules.ThrustAllocator import ThrustAllocator
from Modules.Controller import Controller
# from Modules.JoystickInterface import JoystickInterface
from Modules.SimulatedInput import SimulatedInput
from Modules.SensorData import SensorData

class Manager:
    def __init__(self):

        # Button mapping vars
        self.buttonMapping = {
            # 'KeypadY': lambda value: self.sendInput(np.array([128, 128, value]), 'torque'),
            # 'KeypadX': lambda value: self.sendInput(np.array([128, value, 128]), 'force'),
            'StickLX': lambda value: self.velocitySetpoint(value, 'linx'),
            'StickLY': lambda value: self.velocitySetpoint(value, 'liny'),
            'StickRX': lambda value: self.velocitySetpoint(value, 'angz'),
            'PSButton': self.exit,
            'Start': lambda value: self.toggleThrust(value, 'Enable'),
            'ButtonSouth': lambda value: self.toggleThrust(value, 'Disable'),
        }

        self.input = {
            'linx': 0,
            'liny': 0,
            'linz': 0,
            'angx': 0,
            'angy': 0,
            'angz': 0,
        }

        # Controller vars
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

        self.T = 1000 # Sample time in ms

        self.Controller = Controller()
        self.joyQ = Queue()

        # joy = JoystickInterface(joyq)
        self.joy = SimulatedInput(self.joyQ)
        self.sensorData = SensorData(self.T/1000) # Initialize sensor reader and kalman filter
        self.thrustAllocator = ThrustAllocator()

        self.running = True
        self.idleMotor = True

    def run(self):

        threads = [self.joy]
        QManager = Thread(target=self.QManager)

        QManager.start()
        for t in threads: t.start()
        self.idleMotor = False # For testing purposes

        thrust = np.array([0]*6)

        while self.running:
            startTime = time()

            self.state = self.sensorData.sample(self.state, thrust) # Sample filter
            thrust = self.Controller.sample(self.state, self.dState) # Sample controller


            if self.idleMotor: thrust = np.array([0]*6) # Stop motors if idle
            self.thrustAllocator.allocateThrust(thrust)

            elapsedTime = (time() - startTime) * 1000 # Elapsed time in ms
            sleepTime = (self.T - elapsedTime) / 1000 # Sleep time in s
            if sleepTime < 0: sleepTime = 0
            print(f'Elapsed time: {elapsedTime:0.2f}ms')
            sleep(sleepTime)

        print('Cleaning up...')
        for t in threads: t.cleanup()
        for t in threads: t.join()
        QManager.join()

        print('Nice and clean')

    def QManager(self):
        while self.running:
            if not self.joyQ.empty(): self.buttonPress(self.joyQ.get())

    def buttonPress(self, btn):
        button, value = btn
        if button in self.buttonMapping:
            self.buttonMapping[button](value)
        
    def toggleThrust(self, btnValue, toggle):
        if btnValue:
            if toggle == 'Enable': self.idleMotor = False
            if toggle == 'Disable': self.idleMotor = True
    
    def velocitySetpoint(self, value, velType):
        extremes = [0, 255]
        median = sum(extremes)/2

        deadzone = 5
        centered = value-median
        # If in deadzone: value = 0
        centered = 0 if centered**2 < deadzone**2 else centered
        normalized = centered/median

        maxVel = 1
        self.input[velType] = normalized*maxVel

        linVel = np.array([self.input['linx'], self.input['liny'], self.input['linz']])
        angVel = np.array([self.input['angx'], self.input['angy'], self.input['angz']])

        self.dState['linVel'] = self.Controller.R(self.state['theta']).T@linVel
        self.dState['angVel'] = angVel

    def exit(self, msg):
        self.running = False


if __name__ == '__main__':
    app = Manager()
    app.run()
    


