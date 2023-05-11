from time import sleep
from queue import Queue
import numpy as np
from Modules.ThrustAllocator import ThrustAllocator
# from Modules.JoystickInterface import JoystickInterface
from Modules.SimulatedInput import SimulatedInput

# Test

#Test 2

class ButtonMapping:
    def __init__(self):
        self.mapping = {
            'KeypadY': lambda value: self.sendForces(np.array([128, 128, value]), 'torque'),
            'KeypadX': lambda value: self.sendForces(np.array([128, value, 128]), 'force'),
            'PSButton': self.exit,
        }

    def buttonPress(self, btn):
        button, value = btn
        if button in self.mapping:
            return self.mapping[button](value)
    
    def sendForces(self, value, axis):
        extremes = [0, 255]
        median = sum(extremes)/2

        deadzone = 5
        desiredForce = value-median
        # If in deadzone: no force
        for i, f in enumerate(desiredForce): desiredForce[i] = 0 if f**2 < deadzone**2 else f

        msg = ['forces', desiredForce, axis]
        return msg

    def exit(self, msg):
        return 'quit'


if __name__ == '__main__':
    joyq = Queue()
    thrustq = Queue()

    # joy = JoystickInterface(joyq)
    joy = SimulatedInput(joyq)
    thrust = ThrustAllocator(thrustq)
    threads = [joy, thrust]
    mapper = ButtonMapping()
    try:
        for t in threads: t.start()
        print('Program started...')
        while True:
            
            if not joyq.empty():
                joymsg = joyq.get()
                action = mapper.buttonPress(joymsg[0])
                if action == 'quit': raise KeyboardInterrupt
                if action: thrustq.put(action)

    except KeyboardInterrupt:
        print('Cleaning up...')
        for t in threads: t.cleanup()
        for t in threads: t.join()
        
    print('Nice and clean')


