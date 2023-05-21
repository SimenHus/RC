from time import sleep
from queue import Queue
import numpy as np
from Modules.ThrustAllocator import ThrustAllocator
# from Modules.JoystickInterface import JoystickInterface
from Modules.SimulatedInput import SimulatedInput

class ButtonMapping:
    def __init__(self, thrustAlloc):
        self.mapping = {
            # 'KeypadY': lambda value: self.sendInput(np.array([128, 128, value]), 'torque'),
            # 'KeypadX': lambda value: self.sendInput(np.array([128, value, 128]), 'force'),
            'StickLX': lambda value: self.velocitySetpoint(value, 'linx'),
            'StickLY': lambda value: self.velocitySetpoint(value, 'liny'),
            'StickRX': lambda value: self.velocitySetpoint(value, 'angz'),
            'PSButton': self.exit,
        }

        self.input = {
            'linx': 0,
            'liny': 0,
            'linz': 0,
            'angx': 0,
            'angy': 0,
            'angz': 0,
        }

        self.ThrustAllocator = thrustAlloc

    def buttonPress(self, btn):
        button, value = btn
        if button in self.mapping:
            return self.mapping[button](value)
    
    def velocitySetpoint(self, value, velType):
        extremes = [0, 255]
        median = sum(extremes)/2

        deadzone = 5
        centered = value-median
        # If in deadzone: value = 0
        centered = 0 if centered**2 < deadzone**2 else centered
        normalized = centered/median

        maxVel = 5
        self.input[velType] = normalized*maxVel

        linVel = np.array([self.input['linx'], self.input['liny'], self.input['linz']])
        angVel = np.array([self.input['angx'], self.input['angy'], self.input['angz']])
        self.ThrustAllocator.changeSetpoint(linVel=linVel, angVel=angVel)

    def exit(self, msg):
        return 'quit'


if __name__ == '__main__':
    joyq = Queue()

    # joy = JoystickInterface(joyq)
    joy = SimulatedInput(joyq)
    thrust = ThrustAllocator()
    threads = [joy, thrust]
    mapper = ButtonMapping(thrust)
    try:
        for t in threads: t.start()
        print('Program started...')
        while True:
            
            if not joyq.empty():
                joymsg = joyq.get()
                action = mapper.buttonPress(joymsg[0])
                if action == 'quit': raise KeyboardInterrupt

    except KeyboardInterrupt:
        print('Cleaning up...')
        for t in threads: t.cleanup()
        for t in threads: t.join()
        
    print('Nice and clean')


