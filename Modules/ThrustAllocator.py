# https://gpiozero.readthedocs.io/en/stable/
# from gpiozero import Motor
from time import sleep


# class DCMotor:
#     'DC Motor driver'
#     def __init__(self, pinIDs):
#         self.Motor = Motor(pinIDs[0], pinIDs[1])

#     def setVoltage(self, V):
#         def sign(x): return 1 if x >=0 else -1
#         if sign(V)*V > 3.3: V = sign(V)*3.3 # Max 3.3V in RSPI pins
#         newDirection = sign(V)
#         currentDirection = sign(self.Motor.value) # Get current motor direction

#         if newDirection*V > 1: V = newDirection*1

#         if newDirection != currentDirection:
#             self.Motor.stop()
#             sleep(0.1)

#         if V == 0: self.Motor.stop()
#         elif newDirection > 0: self.Motor.forward(V)
#         elif newDirection < 0: self.Motor.backward(V)

#     def cleanup(self):
#         self.Motor.stop()

class ThrustAllocator:

    def __init__(self):

        # Motor driver initialization
        motorRightPins = [12, 16] # Dummy pins
        motorLeftPins = [22, 10] # Dummy pins
        # self.Motor1 = DCMotor(motorRightPins)
        # self.Motor2 = DCMotor(motorLeftPins)
        # self.Motors = [self.Motor1, self.Motor2]

        # Motor params
        self.Kf = 1 # Motor force const
        self.fd = 0 # Linear friction
        self.td = 0 # Rotational friction
        
        # System params
        self.rw = 1 # Dist from CoG to wheel

    def allocateThrust(self, thrust):

        # Motor calculations
        Vs = (thrust[5] + self.td)/(self.Kf*self.rw)
        Vd = (thrust[1] + self.fd)/self.Kf

        V1 = 1/2*(Vs + Vd)
        V2 = 1/2*(Vs - Vd)

        Volts = [V1, V2]
        print(f'\n\n--- Motor 1 ----- Motor 2 ---')
        print(f'--- {V1} ----- {V2} ---')
        # for V, motor in zip(Volts, self.Motors): motor.setVoltage(V)


    def cleanup(self):
        # for motor in self.Motors: motor.cleanup()
        pass
