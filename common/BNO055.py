
import numpy as np
from dataclasses import dataclass

from IMUGeneral import EulerFromIMU


@dataclass
class BNO055Data:
    """Class to store data read from BNO055 sensor
    
    Args:
        acc (ndarray[3, n]): Accelerometer data m/s^2
        mag (ndarray[3, m]): Magnetometer data micro-tesla
        gyro (ndarray[3, k]): Gyroscope data rad/s
    """

    acc: 'np.ndarray[3]'
    mag: 'np.ndarray[3]'
    gyro: 'np.ndarray[3]'


    def EulerAngles(self) -> 'np.ndarray[3]':
        """Return Euler angles from sensor data
        """
        return EulerFromIMU(self.acc, self.mag)