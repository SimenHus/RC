# https://www.electronicoscaldas.com/datasheet/ULN2003A-PCB.pdf
# https://gpiozero.readthedocs.io/en/stable/
from gpiozero import DigitalOutputDevice

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
    def __init__(self):
        pass
    # Legg til strøm kontroll ved endring av polaritet