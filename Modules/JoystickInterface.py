from evdev import InputDevice, ecodes
from multiprocessing import Process

class JoystickInterface(Process):
    def __init__(self, queue):
        super().__init__()
        self.gamepad = InputDevice('/dev/input/event3')

        # Map button value to name
        self.buttons = {
            0: 'StickLX',
            1: 'StickLY',
            2: 'L2Analog',
            3: 'StickRX',
            4: 'StickRY',
            5: 'R2Analog',
            16: 'KeypadX',
            17: 'KeypadY',
            304: 'ButtonSouth',
            305: 'ButtonEast',
            307: 'ButtonNorth',
            308: 'ButtonWest',
            310: 'L1',
            311: 'R1',
            312: 'L2Digital',
            313: 'R2Digital',
            314: 'Select',
            315: 'Start',
            316: 'PSButton',
            317: 'L3',
            318: 'R3',
        }

        # Threading variables
        self.queue = queue
        self.daemon = True
        self.running = True

    def run(self):
        self.queue.put('ready')
        for event in self.gamepad.read_loop():
            if not self.running: break
            if event.type == ecodes.EV_SYN: continue
            msg = False
            disableAnalog = True

            button, val = event.code, event.value

            if disableAnalog and button < 6: continue
            if button in self.buttons: msg = True

            if msg: self.queue.put([[self.buttons[button], val], self.name])

    def cleanup(self):
        self.running = False