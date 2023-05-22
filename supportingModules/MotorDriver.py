# https://www.electronicoscaldas.com/datasheet/ULN2003A-PCB.pdf
# https://gpiozero.readthedocs.io/en/stable/
from gpiozero import DigitalOutputDevice, Motor
from time import sleep

class ULN2003A:
    'ULN2003A PCB motor driver'
    def __init__(self, pinIDs, defaultDirection=1):
        self.pins = {
            0: DigitalOutputDevice(pinIDs[0]), # IN4
            1: DigitalOutputDevice(pinIDs[1]), # IN3
            2: DigitalOutputDevice(pinIDs[2]), # IN2
            3: DigitalOutputDevice(pinIDs[3]), # IN1
            }
        self.steps = [
            # [0, 0, 0, 1], # A
            [0, 0, 1, 1], # AB
            # [0, 0, 1, 0], # B
            [0, 1, 1, 0], # BC
            # [0, 1, 0, 0], # C
            [1, 1, 0, 0], # CD
            # [1, 0, 0, 0], # D
            [1, 0, 0, 1], # DC
        ]
        self.currentStep = 0
        self.defaultDirection = defaultDirection

    def drive(self, reverse=False):
        stepChange = -self.defaultDirection if reverse else self.defaultDirection
        nextStep = (self.currentStep + stepChange) % len(self.steps)

        for pin, pinValue in enumerate(self.steps[nextStep]):
            if pinValue: self.pins[pin].on()
            else: self.pins[pin].off()
        self.currentStep = nextStep

    def cleanup(self):
        for key, pin in self.pins.items(): pin.off()
        


class DCMotor:
    'DC Motor driver'
    def __init__(self, pinIDs):
        self.Motor = Motor(pinIDs[0], pinIDs[1])

    def setVoltage(self, V):
        def sign(x): return 1 if x >=0 else -1
        V = V/3.3 # Max 3.3V in RSPI pins
        newDirection = sign(V)
        currentDirection = sign(self.Motor.value) # Get current motor direction

        if newDirection*V > 1: V = newDirection*1

        if newDirection != currentDirection:
            self.Motor.stop()
            sleep(0.1)

        if V == 0: self.Motor.stop()
        elif newDirection > 0: self.Motor.forward(V)
        elif newDirection < 0: self.Motor.backward(V)


    def cleanup(self):
        self.Motor.stop()
        # Legg til strøm kontroll ved endring av polaritet