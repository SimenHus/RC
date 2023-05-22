import threading
from pynput import keyboard
from pynput.keyboard import Key
from time import sleep

class SimulatedInput(threading.Thread):
    def __init__(self, queue):
        super().__init__(name='Joy')

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

        self.keyPressed = False

        # Threading variables
        self.queue = queue
        self.daemon = True
        self.running = True

    def onPress(self, key):
        if self.keyPressed: pass
        elif key == Key.up:
            self.queue.put([[self.buttons[0], 255], self.name])
            self.keyPressed = True
        elif key == Key.down:
            self.queue.put([[self.buttons[0], 0], self.name])
            self.keyPressed = True
        elif key == Key.left:
            self.queue.put([[self.buttons[1], 0], self.name])
            self.keyPressed = True
        elif key == Key.right:
            self.queue.put([[self.buttons[1], 255], self.name])
            self.keyPressed = True
        

    def onRelease(self, key):
        self.keyPressed = False
        if key == Key.right or key == Key.left: self.queue.put([[self.buttons[1], 128], self.name])
        if key == Key.up or key == Key.down: self.queue.put([[self.buttons[0], 128], self.name])
        if key == Key.esc: self.queue.put([[self.buttons[316], 1], self.name])

    def run(self):
        listener = keyboard.Listener(on_press=self.onPress, on_release=self.onRelease)
        listener.start()

        print('Keyboard listener ready...')
        while self.running: sleep(1)
        listener.join()

    def cleanup(self):
        self.running = False