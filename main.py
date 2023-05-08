from time import sleep
import threading
from queue import Queue

from Modules.ThrustAllocator import ThrustAllocator
from Modules.JoystickInterface import JoystickInterface



class ButtonMapping:
    def __init__(self):
        self.mapping = {
            'KeypadY': self.driveControl,
            'KeypadX': lambda x: self.driveControl(x, turn=True),
            'PSButton': self.exit,
        }

    def buttonPress(self, btn):
        button, value = btn
        if button in self.mapping:
            return self.mapping[button](value)
    
    def driveControl(self, value, turn=False):
        msg = ['driving', -value, turn]
        return msg

    def exit(self, msg):
        return 'quit'


if __name__ == '__main__':
    joyq = Queue()
    thrustq = Queue()

    joy = JoystickInterface(joyq)
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


