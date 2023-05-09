from time import sleep
from queue import Queue

from Modules.ThrustAllocator import ThrustAllocator
from Modules.JoystickInterface import JoystickInterface

# Test

#Test 2

class ButtonMapping:
    def __init__(self):
        self.mapping = {
            'KeypadY': lambda value: self.thrustMsg(value, 'y'),
            'KeypadX': lambda value: self.thrustMsg(value, 'x'),
            'PSButton': self.exit,
        }

    def buttonPress(self, btn):
        button, value = btn
        if button in self.mapping:
            return self.mapping[button](value)
    
    def thrustMsg(self, value, axis):
        msg = ['thrust', value, axis]
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


