from supportingModules.MotorDriver import ULN2003A
from time import sleep
import threading

class ThrustAllocator(threading.Thread):

    def __init__(self, queue):
        super().__init__(name='Thrust')
        # IN4, IN3, IN2, IN1. Number refers to GPIO pin number
        motor1Pins = [12, 16, 20, 21]
        motor2Pins = [26, 19, 13, 6]
        motor3Pins = [22, 10, 9, 11]
        motor4Pins = [24, 25, 8, 7]
        self.MotorFR = ULN2003A(motor1Pins)
        self.MotorBL = ULN2003A(motor2Pins)
        self.MotorFL = ULN2003A(motor3Pins)
        self.MotorBR = ULN2003A(motor4Pins)
        self.Motors = [self.MotorFR, self.MotorFL, self.MotorBR, self.MotorBL]
        
        self.driveState = 0
        self.turning = False

        # Threading variables
        self.queue = queue
        self.daemon = True
        self.running = True

    def run(self):
        while self.running:
            if not self.queue.empty(): self.readmsg(self.queue.get())

            currentState = self.driveState

            if currentState and self.turning: self.turn(currentState)
            elif currentState: self.driveStraight(currentState)

            sleep(0.002)

    def driveStraight(self, direction):
        forward = True if direction > 0 else False
        self.MotorFR.drive(reverse=forward)
        self.MotorBR.drive(reverse=forward)
        self.MotorFL.drive(reverse=not forward)
        self.MotorBL.drive(reverse=not forward)
        if forward: print('Driving forwards')
        else: print('Driving backwards')


    def turn(self, direction):
        reverse = False if direction > 0 else True
        for motor in self.Motors: motor.drive(reverse=reverse)
        if reverse: print('Turning left')
        else: print('Turning right')

    def readmsg(self, msg):
        action, value, turn = msg
        if action == 'driving':
            self.turning = turn
            self.driveState = value

    def cleanup(self):
        for motor in self.Motors: motor.cleanup()
        self.running = False


