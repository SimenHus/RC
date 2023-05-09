from supportingModules.MotorDriver import DCMotor
from time import sleep
import threading

class ThrustAllocator(threading.Thread):

    def __init__(self, queue):
        super().__init__(name='Thrust')

        # Motor driver initialization
        motorRightPins = [12, 16] # Dummy pins
        motorLeftPins = [22, 10] # Dummy pins
        self.MotorR = DCMotor(motorRightPins)
        self.MotorL = DCMotor(motorLeftPins)
        self.Motors = [self.MotorR, self.MotorL]


        self.desiredThrust = {
            'x': 0,
            'y': 0,
        }

        # Threading variables
        self.queue = queue
        self.daemon = True
        self.running = True

    def run(self):
        while self.running:
            if not self.queue.empty(): self.readmsg(self.queue.get())

            self.allocateThrust()

    def allocateThrust(self):
        
        # Normalize thrust input to -1 , 1
        extremes = [0, 255]

        def norm(value):
            return 2*value/(extremes[1] - extremes[0]) - 1
        deadzone = 5
        thrust = [norm(_) for _ in self.desiredThrust]
        # If within deadzone -> thrust = 0
        for ax in thrust: ax = 0 if ax**2 < norm(deadzone)**2 else ax

        # Legg til strøm kontroll ved motsatt polaritet
        print(f'Motor thrust: {thrust}')

    def readmsg(self, msg):
        action, value, comment = msg
        if action == 'thrust':
            self.desiredThrust[comment] = value

    def cleanup(self):
        for motor in self.Motors: motor.cleanup()
        self.running = False


